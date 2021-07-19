import json
import io
import random
import urllib.parse

from datetime import datetime
from typing import Dict, List, Optional
from zipfile import ZipFile

import numpy as np
import pandas as pd
import kglab
import rdflib
import requests

from fastcore.foundation import L

NAMESPACES = {
    "bf": "http://id.loc.gov/ontologies/bibframe/",
    "bflc": "http://id.loc.gov/ontologies/bflc/",
    "mads": "http://www.loc.gov/mads/rdf/v1#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "sinopia": "http://sinopia.io/vocabulary/"
}

BIBFRAME = rdflib.Namespace("http://id.loc.gov/ontologies/bibframe/")
SINOPIA = rdflib.Namespace("http://sinopia.io/vocabulary/")

def create_kg(sinopia_uri: str, name: str = "Sinopia Knowledge Graph") -> kglab.KnowledgeGraph:
    if sinopia_uri.endswith("zip"):
        rdf_graph = from_zip_url(sinopia_uri)
    else:
         rdf_graph = harvest(sinopia_uri)
    return kglab.KnowledgeGraph(
        name =  name,
        namespaces=NAMESPACES,
        import_graph=rdf_graph
    )

def harvest(api_url: str) -> rdflib.Graph:
    """Takes a Sinopia API endpoint URI, extracts each resource and
    template, and returns a dictionary with two lists, a resources and a
    templates, and the total number of resources harvested from the api.

    @param api_url -- URI to Sinopia API endpoint
    """
    def add_resource(resource):
        if not 'data' in resource:
            print(f"\n{resource.get('uri')} missing data")
            return
        jsonld = json.dumps(resource.pop("data")).encode()
        try:
            nt_rdf = preprocess(jsonld, resource.get('uri'))
            graph.parse(data=nt_rdf, format="nt")
        except Exception as error:
            print(f"Failed to parse {resource}\n{error}")
            return
    count = 0
    graph = rdflib.Graph()
    for ns, uri in NAMESPACES.items():
        graph.namespace_manager.bind(ns, uri)
    initial = requests.get(api_url)
    for row in initial.json().get("data"):
        add_resource(row)
    next_link = initial.json().get("links").get("next")
    if next_link is None:
        return graph
    while 1:
        result = requests.get(next_link)
        if result.status_code > 300:
            break
        payload = result.json()
        new_next = payload.get("links").get("next")
        if new_next is None:
            new_text = payload.get("links").get("first")
        if new_next == next_link or new_next is None:
            break
        for row in payload.get("data"):
            add_resource(row)
            if not count%25 and count > 0:
                print(".", end="")
            if not count%100:
                print(f"{count:,}", end="")
            count += 1
        next_link = new_next
    return graph
        
def preprocess(jsonld: str, resource_uri: str) -> str:
    graph = rdflib.Graph()
    graph.parse(data=jsonld, format='json-ld')
    for s,p,o in graph:
        if isinstance(s, rdflib.URIRef) and not rdflib.term._is_valid_uri(s):
            new_s = fix_invalid_url(s)
            for pred, obj in graph.predicate_objects(s):
                graph.remove((s,pred,obj))
                graph.add((new_s,pred,obj))
        if isinstance(o, rdflib.URIRef) and not rdflib.term._is_valid_uri(o):
            new_o = fix_invalid_url(o)
            for subj, pred in graph.subject_predicates(o):
                graph.remove((subj, pred, o))
                graph.add((subj, pred, new_o))
    # Need for downstream ML applications to have unique bnodes
    resource_parts = urllib.parse.urlsplit(resource_uri)
    basepath = f"{resource_parts.path}#"
    graph = graph.skolemize(authority=resource_uri,
                            basepath=basepath)
    return graph.serialize(format='nt').decode()

def fix_invalid_url(uri: rdflib.URIRef) -> rdflib.URIRef:
    """Parses URI and attempts to quote parts in order to create valid URI
    
    @param uri -- URIRef
    """
    parse_result = urllib.parse.urlsplit(str(uri))
    fixed_parts = (parse_result.scheme,
                   parse_result.netloc,
                   urllib.parse.quote_plus(parse_result.path),
                   urllib.parse.quote_plus(parse_result.query),
                   urllib.parse.quote_plus(parse_result.fragment))
    fixed_url = urllib.parse.urlunsplit(fixed_parts)
    return rdflib.URIRef(fixed_url)

def predicate_row(subject: rdflib.URIRef, graph: rdflib.Graph) -> dict:
    """Returns a dictionary of weighted predicates using a subject

    @param subject -- Subject URI
    @param graph -- RDF graph
    """
    output = { 'uri': str(subject) }
    predicates = [pred for pred in graph.predicates(subject=subject)]
    for predicate in predicates:
        # Use value of sinopia:hasResourceTemplate as our dependent variable
        if predicate == SINOPIA.hasResourceTemplate:
            template_name = str(graph.value(subject=subject, predicate=predicate))
            output['template'] = str(graph.value(subject=subject, predicate=predicate))
        pred_key = str(predicate)
        if pred_key in output:
            output[pred_key] += 1.
        else:
            output[pred_key] = 1.
    return output

def create_splits(df, valid_pct=0.2):
    train, valid = L(), L()
    for row_values in df.groupby("template").indices.values():
        # Shuffle group
        random.shuffle(row_values)
        # Ensure template is present in both training and validation data
        train.append(row_values[0])
        valid.append(row_values[1])
        # Iterate through the rest of the group and add to train and valid lists
        # based on valid percentage
        for i, v in enumerate(row_values):
            if i < 2:
                continue
            if random.random() <= valid_pct:
                valid.append(v)
            else:
                train.append(v)
    return (train, valid)
          
def get_matches(text: str, 
                nlp, 
                matcher, 
                lookup_df,
                max_matches=None):
    """Returns matches for a text string using a  spaCy phrase matcher
    
    @param text -- Text
    @param nlp -- spaCy NLP pipeline
    @param matcher -- spaCy Phrase Matcher
    @param lookup_df -- source Pandas dataframe used to populate phrase matcher
    @param max_matches -- maximum matches to return, default is None (returns everything)
    """
    matches = []
    doc = nlp(text)
    for match_id, _start, _end in matcher(doc):
        lookup_url = nlp.vocab.strings[match_id]
        lookup_name = lookup_df[lookup_df['URL'] == lookup_url].iloc[0]["name"]
        matches.append((lookup_url, lookup_name))
        if max_matches is not None and len(matches) >= max_matches:
            break
    return matches
        

VIAF_URL_TEMPLATE = """http://www.viaf.org/viaf/search?query=cql.any+=+"{term}"&maximumRecords=5&httpAccept=application/json"""

def viaf_people_search(term):
    viaf_url = VIAF_URL_TEMPLATE.format(term=term)
    viaf_result = requests.get(viaf_url)
    output = {}
    if viaf_result.status_code < 300:
        records = viaf_result.json().get('searchRetrieveResponse', {}).get('records', [])
        for row in records:
            name_type = row["record"]["recordData"]["nameType"]
            if not name_type.startswith("Personal"):
                continue
            viaf_authority_url = row["record"]["recordData"]["Document"]["@about"]
            main_headings = row["record"]["recordData"]["mainHeadings"]["data"]
            if isinstance(main_headings, list):
                first_heading = main_headings[0]
            else:
                first_heading = main_headings
            if viaf_authority_url in output:
                output[viaf_authority_url].append(first_heading.get('text'))
            else:
                output[viaf_authority_url] = [first_heading.get('text')]
    return output
            
    