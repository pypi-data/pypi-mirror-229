from __future__ import annotations

import simplejson as json
import logging
from functools import cached_property
import dash_mantine_components as dmc
from dash_extensions.enrich import Output, Input, State, html, dcc, Trigger, no_update, DashLogger
from dash_blueprints.aio.base import BlueprintBase
from dash_blueprints.utils import options, report_dash_exception
from swarkn.helpers import is_local

logger = logging.getLogger(__name__)

class Favourites(BlueprintBase):
    COMPONENT_KWARGS = dict(clearable=True, persistence=True, searchable=True)
    DEFAULT_SELECTION = 'default'

    def _components(self):
        self.id_store = self.ids('store')

    def init(self,
             in_component: tuple[str | dict, str],
             out_component: tuple[str | dict, str] = None,
             load_title: str = None,
             save_title: str = None,
             root='dash_blueprints'
    ):
        self.in_component = in_component
        self.out_component = out_component or in_component
        self.load_title = load_title or f'Load {self.id}: '
        self.save_title = save_title or f'Save {self.id}: '
        self.root = root

    def build_layout(self):
        return html.Div(self.loader + self.saver, className='h-ctrl')

    def path(self, shared=True):
        filename = 'shared' # TODO implement user
        return f"{self.root}/{self.id}/{filename}"

    @cached_property
    def loader(self):
        return [
            dmc.Checkbox(id=self.ids('shared'), label='public ', persistence=True, checked=True),
            dcc.Location(self.ids('url'), refresh=False),
            dcc.Store(self.id_store, storage_type='local'),
            dmc.Select(id=self.ids('dropdown'), value=self.DEFAULT_SELECTION, label=self.load_title, className='h-ctrl',
                **self.COMPONENT_KWARGS),
        ]


    @cached_property
    def saver(self):
        return [
            dmc.Select(id=self.ids('save-input'), placeholder=self.save_title, creatable=True, **self.COMPONENT_KWARGS),
            html.Button('save', id=self.ids('save-button'), className='r-align-abs'),
        ]

    ################################ CALLBACKS ################################

    @property
    def cb_get_saved(self):
        return [Output(self.ids('notify'), 'data'), Output(*self.out_component),
                Input(self.ids('dropdown'), 'value'), State(self.ids('shared'), 'checked')], dict(
                prevent_initial_call=False)
    def get_saved(self, key: str, shared: bool):
        if key:
            try:
                res = self.read(key, shared)
                return no_update, res
            except Exception as e:  # dashlogger doesn't work with dicts
                return ('error', str(e)), no_update
        return no_update, None

    @property
    def cb_load_options(self):
        return [Output(self.ids(x), 'data') for x in ('dropdown', 'save-input')] + [
                Trigger(self.ids('trigger-options'), 'data'), Input(self.ids('shared'), 'checked')], dict(
                log=True, prevent_initial_call=False)
    def load_options(self, shared: bool, dash_logger: DashLogger):
        with report_dash_exception(dash_logger, 'warning'):
            keys = self.list_keys(shared)
            return [options(keys)] * 2
        return [], []

    @property
    def cb_save_state(self):
        return [Output(self.ids('trigger-options'), 'data'), Trigger(self.ids('save-button'), 'n_clicks'),
                State(*self.in_component), State(self.ids('save-input'), 'value'), State(self.ids('shared'), 'checked')], \
            dict(log=True)
    def save_state(self, obj, key: str, shared: bool, dash_logger: DashLogger):
        with report_dash_exception(dash_logger):
            self.write(obj, key, shared)
            dash_logger.info(f'saved favourite {key} to {"public" if shared else "private"} space')
            return True
        return no_update

    @property #HACK needs to live separately coz log=True callbacks can't output dicts :(
    def cb_notify(self):
        return [Input(self.ids('notify'), 'data')], {'log': True}
    def notify(_self, msg: str, dash_logger: DashLogger):
        if msg:
            type_, text = msg
            getattr(dash_logger, type_)(text)


    ################## overridable io per storage type #####################
    def read(self, key: str, shared: bool) -> dict | list: #must be json serializable
        raise NotImplementedError

    def write(self, obj, key: str, shared: bool) -> dict:
        raise NotImplementedError

    def list_keys(self, shared: bool) -> list[str]:
        raise NotImplementedError

class FavouritesS3(Favourites):
    BUCKET = 'esop-testbucket' # 'change_me_set_this_bucket' # 'esop-test-bucket'

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        import boto3
        if False: #is_local():
            # simulate s3 behavior with local filesystem for testing
            from moto import mock_s3
            mock = mock_s3()
            mock.start()
            self.s3 = boto3.resource('s3')
            self.s3.Bucket(self.BUCKET).create()
        else:
            self.s3 = boto3.resource('s3')

    def get_object(self, key: str, shared: bool):
        return self.s3.Object(self.BUCKET, f'{self.path(shared)}/{key}')

    def read(self, key: str, shared: bool) -> dict | list:
        s3obj = self.get_object(key, shared)
        contents = s3obj.get()['Body'].read()
        jsonstr = contents.decode('utf-8')
        res = json.loads(jsonstr)
        return res

    def write(self, obj, key: str, shared: bool) -> dict:
        s3obj = self.get_object(key, shared)
        to_save = json.dumps(obj)
        res = s3obj.put(Body=to_save)
        return res

    def list_keys(self, shared: bool) -> list[str]:
        itr = self.s3.Bucket(self.BUCKET).objects.filter(Prefix=self.path(shared))
        keys = [obj.key.split('/')[-1] for obj in itr]
        return keys


