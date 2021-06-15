
import pathlib

import ipywidgets as widgets

data = pathlib.Path("data")

data_dropdown = widgets.Dropdown(
    options=[row.name for row in data.iterdir()],
    description='Data Files',
    disabled=False
)
