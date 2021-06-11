import json
from datetime import datetime
from typing import Dict, List, Optional

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

def kg(api_uri: str, name: str = "Sinopia Knowledge Graph") -> kglab.KnowledgeGraph:
    rdf_graph = harvest(api_uri)
    return kglab.KnowledgeGraph(
        name =  name,
        namespaces=NAMESPACES,
        import_graph=rdf_graph
    )

def harvest(api_url: str) -> Dict:
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