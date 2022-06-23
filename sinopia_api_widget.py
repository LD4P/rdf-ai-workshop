import json

import js

def _environment_checkbox(env):
    div = js.document.createElement("div")
    div.classList.add("form-check")
    ident = env[1]
    radio = js.document.createElement("input")
    radio.setAttribute("type", "radio")
    radio.setAttribute("name", "sinopia_env")
    radio.setAttribute("id", ident)
    radio.classList.add("form-check-input")
    if env[0].startswith("Development"):
        radio.setAttribute("checked", "")
    div.appendChild(radio)
    label = js.document.createElement("label", env[0])
    label.setAttribute("for", ident)
    label.classList.add("form-check-label")
    label.innerHTML = env[0]
    div.appendChild(label)
    return div

def _group_select(options: list=[]):
    select = js.document.createElement("select")
    select.setAttribute("id", "env-groups")
    return select



def sinopia_api(widget_div):
    widget_div.element.classList.add("row")
    env_column = js.document.createElement("div")

    for env in [
        ("Development", "https://api.development.sinopia.io/"),
        ("Stage", "https://api.stage.sinopia.io/"),
        ("Production", "https://api.sinopia.io/"),
    ]:
        env_checkbox = _environment_checkbox(env)
        env_column.appendChild(env_checkbox)
        
    widget_div.element.appendChild(env_column)
    widget_div.element.appendChild(_group_select())
