import logging
import os, sys
from contextlib import contextmanager
from functools import partial
from typing import Iterable, Any, Callable
import pandas as pd
from dash import dcc
from dash_extensions.enrich import no_update, MATCH, ALLSMALLER, ALL, html
from swarkn.helpers import freeze, unfreeze

logger = logging.getLogger(__name__)
DF = pd.DataFrame
def cid(type: str, index=MATCH) -> dict:
    """syntax sugar for pattern matched ids"""
    return dict(type=type, index=index)

def options(iter: Iterable):
    if isinstance(iter, (dict, pd.Series)):
        return [{'label': k, 'value': v} for k, v in iter.items()]
    return [{'label': r, 'value': r} for r in iter]

@contextmanager
def report_dash_exception(dash_logger, log_level: str = 'error', template='{}', **logger_kwags):
    try:
        yield
    except Exception as ex:
        msg = template.format(ex)
        getattr(logging, log_level)(msg, exc_info=True)
        getattr(dash_logger, log_level)(msg, **logger_kwags)  # TOOD move to context manager


def wrap_label(component, *preargs, wrapper_class='label-wrapper', posn='t', **prekwargs):
    """
    :param posn str: t b l r, top bottom left right. defualts to top
    """
    from dash import html
    #TODO: use style to determine position of label
    linebreak = '' if posn in 'lr' else html.Br()
    return lambda label, *args, **kwargs: html.Div([
        html.Label(label),
        linebreak,
        component(*(preargs + args), **(prekwargs | kwargs)),
    ], className=wrapper_class)

def init_stores(app):
    """
    looks through all callback components that don't exist in layout and instantiates them into dcc.stores
    """

    cb_components = {freeze(x.component_id)
        for comp in app.blueprint.callbacks
            for x in list(comp.inputs) + list(comp.outputs)
    if x.component_property == 'data' and (
       not isinstance(x.component_id, dict) or x.component_id['index'] not in {MATCH, ALL, ALLSMALLER}
    )}

    layout_components = {freeze(x.id) for x in app.layout._traverse_ids()}
    remainder = [unfreeze(x) for x in cb_components - layout_components]
    if remainder:
        logger.info(f'adding missing stores {remainder}')
        app.layout = html.Div([app.layout, *[dcc.Store(x) for x in remainder]])