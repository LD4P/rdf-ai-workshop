import markdown

def render_mkdwn(element):
    raw_mkdwn = element.element.innerHTML
    element.clear()
    element.element.innerHTML = markdown.markdown(raw_mkdwn)    
