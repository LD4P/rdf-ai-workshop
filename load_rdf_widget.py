import json

import js
import rdflib

from jinja2 import Template
from pyodide import create_proxy
from pyodide.http import open_url

from helpers import NAMESPACES, sinopia_graph


def _build_graph(event) -> rdflib.Graph:
    bf_elements = js.document.querySelectorAll(".bf-entity")
    js.console.log(bf_elements)
    urls = [element.value for element in bf_elements]

    for url in urls:
        result = open_url(url)
        sinopia_json_ld = json.loads(result.getvalue())['data']
        sinopia_graph.parse(data=json.dumps(sinopia_json_ld),
                            format='json-ld')
    _summarize_graph(sinopia_graph)

bf_summary_template = Template("""<table class="table">
  <thead>
     <tr>
        <th>Description</th>
        <th>Value</th>
     </tr>
  </thead>
  <tbody>
     <tr>
        <td>Total Triples</td>
        <td>{{ graph|length }}</td>
     </tr>
     <tr>
        <td>Subjects</td>
        <td>{{ []|length }}</td>
     </tr>
     <tr>
        <td>Predicates</td>
        <td>{{ []|length }}</td>
     </tr>
     <tr>
        <td>Objects</td>
        <td>{{ []|length }}</td>
     </tr>
  </tbody>
</table>
<div class="mb-3">
  <div class="dropdown">
    <button class="btn btn-secondary dropdown-toggle" 
            type="button" 
            data-bs-toggle="dropdown"
            id="rdf-download-file"
            aria-expanded="false">
      Download Graph
    </button>
    <ul class="dropdown-menu" aria-labelledby="rdf-download-file">
        <li><a class="dropdown-item" href="#">Turtle (.ttl)</a></li>
        <li><a class="dropdown-item" href="#">XML (.rdf)</a></li>
        <li><a class="dropdown-item" href="#">JSON-LD (.json)</a></li>
         <li><a class="dropdown-item" href="#">N3 (.nt)</a></li>
    </ul>
  </div>
</div>
""")

def _summarize_graph(graph: rdflib.Graph):
    summary_div = js.document.getElementById("summarize-work-instance-item")
    # graph.query("""SELECT DISTINCT count(?s) count(?p) count(?o) 
    # WHERE { ?s ?p ?o . }""")
    summary_div.innerHTML = bf_summary_template.render(graph=graph)


bf_template = Template("""<div class="col">
{% for bf_entity in entities %}
  {% set id = bf_entity[1].split("/")[-1] %}
  <div class="mb-3">
    <label for="{{ id }}" class="col-form-label">BIBFRAME {{ bf_entity[0] }} URL</label> 
    <input type="text" id="{{ id }}" class="form-control bf-entity" value="{{ bf_entity[1] }}">
  </div>
{% endfor %}
  <button type="button" id="build-graph-btn" class="btn btn-primary">Build RDF Graph</button>
</div>""")

def bibframe(element_id: str, urls: list):
    form_element = js.document.getElementById(element_id)
    form_element.classList.add("col")
    entities = zip(("Work", "Instance", "Item"), urls)
    form_element.innerHTML = bf_template.render(entities=entities)
    button = js.document.getElementById("build-graph-btn")
    button.addEventListener("click", create_proxy(_build_graph))


sparql_template = Template("""<div class="mb-3">
    <label for="bf-sparql-queries" class="form-label">SPARQL Query</label>
    <textarea class="form-control" id="bf-sparql-queries" row="10">
     {% for ns in namespaces %}PREFIX {{ ns[0] }}: <{{ ns[1] }}>\n{% endfor %}
    </textarea>
  </div>
  <div class="mb-3">
    <button class="btn btn-primary">Run query</button>
  </div>
</div>""")

def bibframe_sparql(element_id: str):
    wrapper_div = js.document.getElementById(element_id)
    wrapper_div.innerHTML = sparql_template.render(namespaces=NAMESPACES)
