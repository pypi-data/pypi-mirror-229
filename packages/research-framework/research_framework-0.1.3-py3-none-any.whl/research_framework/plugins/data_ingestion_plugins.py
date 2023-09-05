from research_framework.container.container import Container
from research_framework.base.plugin.base_plugin import BasePlugin
import pandas as pd

from research_framework.pipeline.wrappers import InputFiterWrapper

@Container.bind(InputFiterWrapper)
class SaaSPlugin(BasePlugin):

    def fit(self, *args, **kwargs): ...

    def predict(self, _, params):
        self.params = params
        obj = Container.storage.download_file(self.params['drive_ref'])
        return obj

    def get__dict__(self):
        return self.params
    
@Container.bind(InputFiterWrapper)
class CSVPlugin(BasePlugin):

    def fit(self, *args, **kwargs): ...

    def predict(self, _, params):
        self.params = params
        obj = pd.read_csv(**params)
        return obj

    def get__dict__(self):
        return self.params
        

