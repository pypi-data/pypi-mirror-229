from abc import ABC
from dash_extensions.enrich import DashBlueprint

class BlueprintBase(ABC):
    def __init__(self, app, id_: str, *args, blueprint=None, **kwargs):

        self.id = id_
        self._components()
        self.blueprint = blueprint or DashBlueprint()
        self.init(*args, **kwargs)
        self.blueprint.layout = self.layout = self.build_layout()
        self.add_callbacks()
        self.blueprint.register_callbacks(app)


    def add_callbacks(self):
        for attr in dir(self):
            if attr.startswith('cb_'):
                prop = getattr(self, attr)
                args, kwargs = (prop + ({},))[:2]
                funcname = attr.replace('cb_', '')
                self.blueprint.callback(*args, **kwargs)(
                    getattr(self, funcname)
                )


    def ids(self, type_: str):
        return f'[{self.id}]-{type_}' #cid(type_, self.id)

    def _components(self):
        pass

    def init(self):
        raise NotImplementedError