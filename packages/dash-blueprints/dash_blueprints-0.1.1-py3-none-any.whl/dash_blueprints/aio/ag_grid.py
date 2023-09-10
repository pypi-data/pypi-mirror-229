from __future__ import annotations
from functools import cached_property
import polars as pl
import pandas as pd
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from dash_ag_grid import AgGrid
from dash_extensions.enrich import Output, Input, State, html, dcc, Trigger, Serverside, no_update, ALL

from dash_blueprints.ag_common import ag_options
from dash_blueprints.aio.base import BlueprintBase
from dash_blueprints.aio.favourites import FavouritesS3
from dash_blueprints.utils import cid

Div = html.Div
DF = pl.DataFrame
DFPd = pd.DataFrame


class AGTable(BlueprintBase):
    AG_OPTIONS = ag_options()
    FavouritesCls = FavouritesS3


    def _components(self):
        self.id_grid = self.ids('grid')
    def init(self, options=None):
        self.options = options or self.AG_OPTIONS
        self.fav = self.FavouritesCls(self.blueprint, f'{self.id}-fav',
            (self.ids("fav"), 'data'), (self.ids("fav-out"), 'data'),
            load_title='Favorite Views: ',
            save_title='Favourite View Name: '
        )

    def build_layout(self):
        return Div([self.bar, self.grid], className='ag-wrap')

    @cached_property
    def grid(self):
        return AgGrid(self.id_grid, **self.options)

    @cached_property
    def bar(self):
        kwargs = dict(
            className='mr-1',
        )
        res = Div(self.fav.loader + [
            html.Button('save view', id=cid('MODAL-OPEN', self.ids('save-view')), **kwargs),
            html.Button('autosize', id=self.ids("autosize"), **kwargs),
            html.Button('clear filter', id=self.ids("clear-filter"), **kwargs),
            dmc.TextInput(id=self.ids("quick-filter"), placeholder='quick filter', size='xs'),
            dmc.Modal(Div(self.fav.saver), id=cid('MODAL', self.ids('save-view')), title="Favourite Views"),
            dcc.Store('test')
        ], className='r-align h-ctrl')
        return res

    @property
    def cb_load_fav(self):
        return [[Output(self.id_grid, x) for x in ('columnState', 'filterModel')],  # 'columnSize' columnDefs
                Input(*self.fav.out_component), *[Trigger(self.id_grid, x) for x in ('rowData', 'columnDefs')]],
    def load_fav(self, saved: list):
        return saved or no_update

    @property
    def cb_save_fav(self):
        return [Output(*self.fav.in_component), *[Input(self.id_grid, x) for x in ('columnState', 'filterModel')]],

    def save_fav(self, colstate, filtermodel):
        return [colstate, filtermodel]

    @property
    def cb_auto_size(self):
        return [Output(self.id_grid, 'columnSize'), Trigger(self.ids('autosize'), 'n_clicks')] + [
                Trigger(self.id_grid, x) for x in ('rowData', 'columnDefs')],  # columnState filterModel 'filterModel',

    def auto_size(self):  # TODO: why is filterModel triggerd when col resized?
        return 'autoSize'

    @property
    def cb_clear_filters(self):
        return [Output(self.id_grid, 'filterModel'), Trigger(self.ids('clear-filter'), 'n_clicks')],

    def clear_filters(self):
        return {}

    @property
    def cb_quick_filter(self):
        return [x(self.id_grid, 'dashGridOptions') for x in (Output, State)] + [
                Input(self.ids('quick-filter'), 'value')],

    def quick_filter(self, options: dict, text: str):
        if text:
            options = options or {}
            options['quickFilterText'] = text
            return options
        raise PreventUpdate

