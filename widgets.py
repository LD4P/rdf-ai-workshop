
import json
import pathlib

import ipywidgets as widgets

data = pathlib.Path("data")

data_dropdown = widgets.Dropdown(
    options=[row.name for row in data.iterdir()],
    description='Data Files:',
    disabled=False
)

sinopia_groups = {
    'All': None,
    'Cornell University': 'cornell',
    'Duke University': 'duke',
    'Frick Art Reference Library': 'frick',
    'Harvard University': 'harvard',
    'Library of Congress': 'dlc',
    'Music Library Association': 'mla',
    'National Library of Medicine': 'nlm',
    'Northwestern University': 'northwestern',
    'PCC': 'pcc',
    'Princeton University': 'princeton',
    'Stanford University': 'stanford',
    'Texas A&M University': 'tamu',
    'University of Alberta': 'alberta',
    'University of California, Davis': 'ucdavis',
    'University of California, San Diego': 'ucsd',
    'University of Chicago': 'chicago',
    'University of Colorado, Boulder': 'boulder',
    'University of Michigan': 'michigan',
    'University of Minnesota': 'minnesota',
    'University of Pennsylvania': 'penn',
    'University of Texas, Austin, Harry Ransom Center': 'hrc',
    'University of Washington': 'washington',
    'Yale': 'yale'
}

sinopia_groups_select = widgets.Select(
   value=None,
   options=sinopia_groups,
   placeholder='Enter Sinopia group',
   description='Group:',
   disabled=False
)

sinopia_env_dropdown = widgets.RadioButtons(
    options=[('Development', 'https://api.development.sinopia.io/'),
             ('Stage', 'https://api.stage.sinopia.io/'),
             ('Production', 'https://api.sinopia.io/')],
    description='Environment:',
    disabled=False
)

def generate_url(env, groups):
    resource_url = f"{env}resource"
    if groups is None:
        print(resource_url)
    else:
        print(f"{resource_url}?group={groups}")


url_output = widgets.interactive_output(
    generate_url, 
    {'env': sinopia_env_dropdown,
     'groups': sinopia_groups_select }
)

sinopia_api_group_widget = widgets.VBox(
    [widgets.HBox([sinopia_env_dropdown, sinopia_groups_select]), url_output]
)

def sinopia_api_group_widget_borked():
    header = widgets.HTML("<h2>Sinopia API URL</h2><h3>Generator</h3>", 
                          layout=widgets.Layout(height='auto'))
    header.style.text_align='center'

    

BF_ENTITIES_QUERY = """PREFIX bf: <>

SELECT ?entity ?pred ?object
WHERE {{
 ?entity rdf:type {bf_class} .
 ?entity ?pred ?object .
}} LIMIT {limit}"""
