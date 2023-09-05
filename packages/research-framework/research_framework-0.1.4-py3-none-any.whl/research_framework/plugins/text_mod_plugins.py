from research_framework.container.container import Container
from research_framework.base.plugin.base_plugin import BasePlugin
from research_framework.pipeline.wrappers import PassThroughFilterWrapper

import pandas as pd


@Container.bind(PassThroughFilterWrapper)
class FilterRowsByNwords(BasePlugin):
    config= {
        "name": "Filter len(row)",
        "image": {
            "size": "w-16 h-10",
            "url": "/img/python.png",
        },
        "params": {
            "upper_cut": 100,
            "lower_cut": 10,
        }
    }

    def __init__(self):
        super().__init__()
        self.evr = None
        
    def fit(self, *args, **kwargs): ...
    
    def predict(self, x, params):
        if 'text' in x:
            ids = []
            xs = []
            labels = []

            x.reset_index()
            for _, sentence in x.iterrows():
                try:
                    if len(str(sentence.text)) > params["lower_cut"] and (len(str(sentence.text)) < params["upper_cut"] or params["upper_cut"] < 0):
                        xs.append(sentence.text)
                        ids.append(sentence.id)
                        labels.append(sentence.label)
                except Exception as ex:
                    
                    print(sentence.text)
                    raise ex
            return pd.DataFrame({
                'id': ids,
                'text': xs,
                'label': labels,
            })
        else:
            raise TypeError("Input should be a list")