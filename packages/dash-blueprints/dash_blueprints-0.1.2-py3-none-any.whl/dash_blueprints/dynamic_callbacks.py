from dash_extensions.enrich import Output, Trigger, callback
from dash_blueprints.utils import cid

@callback(Output(cid('MODAL'), 'opened'), Trigger(cid('MODAL-OPEN'), 'n_clicks'))
def modal_open():
    return True