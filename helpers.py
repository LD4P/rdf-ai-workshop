import json
import io
from datetime import datetime
from typing import Dict, List, Optional
from zipfile import ZipFile


import pandas as pd

import kglab
import rdflib
import requests

NAMESPACES = {
    "bf": "http://id.loc.gov/ontologies/bibframe/",
    "bflc":"",
    "mads": "http://www.loc.gov/mads/rdf/v1#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "sinopia": "http://sinopia.io/vocabulary/"
}

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
            graph.parse(data=jsonld, format="json-ld")
        except Exception as error:
            print(f"Failed to parse {resource}\n{error}")
            return
    graph = rdflib.Graph()
    graph.namespace_manager.bind("sinopia", SINOPIA)
    initial = requests.get(api_url)
    for row in initial.json().get("data"):
        add_resource(row)
    next_link = initial.json().get("links").get("next")
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
        next_link = new_next
    return graph

def from_zip_url(zip_url: str) -> rdflib.Graph:
    """Takes the url to the export zip file from a Sinopia environment, extracts all
    RDF and returns an instance of the Knowledge Graph

    @param zip_url -- URL to the zip export file
    """
    zip_result = requests.get(zip_url)
    graph = rdflib.Graph()
    with ZipFile(io.BytesIO(zip_result.content)) as zip_file:
        for zip_info in zip_file.infolist():
            if zip_info.file_size < 1 or zip_info.filename.endswith('log'):
                continue
            with zip_file.open(zip_info) as zip_extract:
                raw_data = zip_extract.read()
                try:
                    resource = json.loads(raw_data)
                    if 'data' in resource:
                        graph.parse(data=json.dumps(resource.get('data')), format='json-ld')
                except  Exception as error:
                    print(f"Failed to parse {zip_info.filename}\n{error}")

    return graph
        
                 
