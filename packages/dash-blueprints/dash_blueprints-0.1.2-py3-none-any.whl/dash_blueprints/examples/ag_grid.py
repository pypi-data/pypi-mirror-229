import logging
from datetime import datetime

import boto3
import dash
import polars as pl
from dash_extensions.enrich import Output, Input, State, html, dcc, Trigger, Serverside, no_update, MATCH, ALL, \
    DashProxy, LogTransform, NoOutputTransform, TriggerTransform, MultiplexerTransform, ServersideOutputTransform

from dash_blueprints.ag_common import ag_options
from dash_blueprints.aio.favourites import FavouritesS3
from swarkn.helpers import init_logger
import dash_blueprints.dynamic_callbacks as dcbs
from dash_blueprints.aio.ag_grid import AGTable
from dash_blueprints.utils import init_stores

boto3.setup_default_session(profile_name='ara', region_name="eu-west-2")
FavouritesS3.BUCKET = 'esop-testbucket'

__ALL__ = [
    dcbs #register dynamic pattern match CBs
]

init_logger()
logger = logging.getLogger(__name__)
Div = html.Div
dt = datetime.fromisoformat


app = DashProxy(__name__,
    transforms=[LogTransform(), NoOutputTransform(), TriggerTransform(), MultiplexerTransform(), ServersideOutputTransform()],
    # external_stylesheets=[dbc.themes.DARKLY],
    prevent_initial_callbacks=True,
    # assets_folder='../assets',
)

table = AGTable(app, 'publish', ag_options() | {'columnDefs': [ #ag_cols(
    {'field': 'hello'},
    {'field': 'world'},
    {'field': 'month', 'aggFunc': 'count'},
]})

app.layout = Div([
    table.layout,
    html.Button('clickme', 'button'),
])

@app.callback(Output(table.id_grid, 'rowData'), Trigger('button', 'n_clicks'))
def set_grid():
    df = pl.DataFrame({
        'hello': [1, 2, 3],
        'world': ['a', 'b', 'c'],
    })
    return df.to_dicts()

init_stores(app)
if __name__ == '__main__':
    app.run_server('0.0.0.0', 8050, debug=True) #debug=True
