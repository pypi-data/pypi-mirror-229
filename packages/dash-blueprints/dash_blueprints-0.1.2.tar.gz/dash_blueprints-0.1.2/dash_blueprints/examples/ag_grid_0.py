
import dash_ag_grid as dag
from dash import Dash, html, Input, Output, State
import pandas as pd

app = Dash(__name__)

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/ag-grid/olympic-winners.csv"
)

columnDefs = [
    {
        "field": "athlete",
        "filter": "agTextColumnFilter",
        "filterParams": {
            "buttons": ["reset", "apply"],
        },
    },
    {
        "field": "age",
        "maxWidth": 100,
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
    },
    {
        "field": "country",
        "filter": "agTextColumnFilter",
        "filterParams": {
            "buttons": ["clear", "apply"],
        },
    },
    {
        "field": "year",
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "cancel"],
            "closeOnApply": True,
        },
        "maxWidth": 100,
    },
    {"field": "sport"},
    {"field": "gold", "filter": "agNumberColumnFilter"},
    {"field": "silver", "filter": "agNumberColumnFilter"},
    {"field": "bronze", "filter": "agNumberColumnFilter"},
    {"field": "total", "filter": "agNumberColumnFilter"},
]

defaultColDef = {
    "flex": 1,
    "minWidth": 150,
    "filter": True,
}

app.layout = html.Div(
    [
        html.Button(id='reset', children='reset'),
        dag.AgGrid(rowData=df.to_dict("records"), columnDefs=columnDefs, columnSize="sizeToFit", id="grid", dashGridOptions={}),
        html.Div(id="out")
    ]
)

app.clientside_callback(
    """
    function(clicks) {
        const grid = document.getElementById("grid");
        const myGrid = FindReact(grid);
        myGrid.state.gridApi.setFilterModel(null);
        return "triggered!";
    }
    """,
    Output('out', 'children'),
    Input('reset', 'n_clicks'),
    prevent_initial_call=True
)

if __name__ == "__main__":
    app.run_server(debug=True)