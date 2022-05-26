import json
import logging
import pathlib

from functools import cache

import requests
import ipywidgets as widgets

data = pathlib.Path("data")

data_dropdown = widgets.Dropdown(
    options=[row.name for row in data.iterdir()],
    description="Data Files:",
    disabled=False,
)


@cache
def get_groups(sinopia_api: str) -> list:
    groups_url = f"{sinopia_api}groups/"
    groups_result = requests.get(groups_url)
    groups = []
    for row in groups_result.json()["data"]:
        groups.append((row["label"], row["id"]))
    return sorted(groups, key=lambda y: y[0])


sinopia_env_dropdown = widgets.RadioButtons(
    options=[
        ("Development", "https://api.development.sinopia.io/"),
        ("Stage", "https://api.stage.sinopia.io/"),
        ("Production", "https://api.sinopia.io/"),
    ],
    description="Environment:",
    disabled=False,
)


sinopia_groups_select = widgets.Select(
    value=None,
    placeholder="Enter Sinopia group",
    description="Group:",
    disabled=False,
)


def update_group_options(change):
    sinopia_groups_select.options = get_groups(change.new)


sinopia_env_dropdown.observe(update_group_options, names="value")


def generate_url(env, groups=None):
    resource_url = f"{env}resource"
    if groups is None:
        print(resource_url)
    else:
        print(f"{resource_url}?group={groups}")


url_output = widgets.interactive_output(
    generate_url, {"env": sinopia_env_dropdown, "groups": sinopia_groups_select}
)

sinopia_api_group_widget = widgets.VBox(
    [widgets.HBox([sinopia_env_dropdown, sinopia_groups_select]), url_output]
)



BF_ENTITIES_QUERY = """PREFIX bf: <>

SELECT ?entity ?pred ?object
WHERE {{
 ?entity rdf:type {bf_class} .
 ?entity ?pred ?object .
}} LIMIT {limit}"""
