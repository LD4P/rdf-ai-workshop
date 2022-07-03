import json
from functools import cache

import js
from pyodide import create_proxy
from pyodide.http import open_url


def _generate_url(event):
    radio_env = js.document.querySelector("input[type='radio']:checked")
    group_url_div = js.document.querySelector("#sinopia-group-url")
    group_url_div.innerHTML = ""
    group_url = f"{radio_env.id}resource"
    if not event.target.value.startswith("all"):
        group_url = f"{group_url}?group={event.target.value}"
    group_anchor = js.document.createElement("a")
    group_anchor.setAttribute("href", group_url)
    group_anchor.innerText = group_url
    group_url_div.appendChild(group_anchor)


@cache
def _get_groups(sinopia_api: str):
    groups_url = f"{sinopia_api}groups/"
    result = open_url(groups_url)
    data = json.loads(result.getvalue())["data"]
    groups = [("All", "all")]
    for row in data:
        groups.append((row["label"], row["id"]))
    return sorted(groups, key=lambda y: y[0])


def _on_load_groups(event):
    group_url_div = js.document.querySelector("#sinopia-group-url")
    group_url_div.innerHTML = ""
    group_select = js.document.querySelector("#env-groups")
    group_select.innerHTML = ""
    groups = _get_groups(event.target.id)
    for group in groups:
        option = js.document.createElement("option")
        option.setAttribute("value", group[1])
        option.innerText = group[0]
        group_select.appendChild(option)


def _environment_checkbox(env):
    div = js.document.createElement("div")
    div.classList.add("form-check")
    ident = env[1]
    radio = js.document.createElement("input")
    radio.setAttribute("type", "radio")
    radio.setAttribute("name", "sinopia_env")
    radio.setAttribute("id", ident)
    radio.classList.add("form-check-input")
    radio.addEventListener("change", create_proxy(_on_load_groups))
    div.appendChild(radio)
    label = js.document.createElement("label", env[0])
    label.setAttribute("for", ident)
    label.classList.add("form-check-label")
    label.innerHTML = env[0]
    div.appendChild(label)
    return div

def _group_select(options: list=[]):
    wrapper_div = js.document.createElement("div")
    wrapper_div.classList.add("col")
    select = js.document.createElement("select")
    select.setAttribute("id", "env-groups")
    select.setAttribute("size", 5)

    select.addEventListener("change", create_proxy(_generate_url))
    wrapper_div.appendChild(select)
    return wrapper_div



def sinopia_api(widget_div):
    widget_div.element.classList.add("row")
    env_column = js.document.createElement("div")
    env_column.classList.add("col")

    for env in [
        ("Development", "https://api.development.sinopia.io/"),
        ("Stage", "https://api.stage.sinopia.io/"),
        ("Production", "https://api.sinopia.io/"),
    ]:
        env_checkbox = _environment_checkbox(env)
        env_column.appendChild(env_checkbox)
        
    widget_div.element.appendChild(env_column)
    widget_div.element.appendChild(_group_select())
    output_div = js.document.createElement("div")
    output_div.setAttribute("id", "sinopia-group-url")
    widget_div.element.appendChild(output_div)

