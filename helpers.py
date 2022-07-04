import js
import markdown
import rdflib

NAMESPACES = [("bf","http://id.loc.gov/ontologies/bibframe/"),
              ("sinopia", "http://sinopia.io/vocabulary/")]

sinopia_graph = rdflib.Graph()

for ns in NAMESPACES:
    sinopia_graph.namespace_manager.bind(ns[0], ns[1])

def render_markdown(element):
    raw_mkdwn = element.element.innerHTML
    element.clear()
    element.element.innerHTML = markdown.markdown(raw_mkdwn)    

def run_step_01(event):
    stage_urls = js.document.querySelector("#sinopia-stage-urls")
    output = js.document.querySelector("#step-01-output")
    raw_input = stage_urls.value
    try:
        exec(raw_input)
        js.console.log(globals())
        output.innerHTML = f"sinopia_urls has ${len(sinopia_stage_urls)}"
    except Exception as e:
        output.innerHTML = f"Error {e} loading {stage_urls.value}"

