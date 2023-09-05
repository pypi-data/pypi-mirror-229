from typing import Dict, Any
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from research_framework.base.plugin.base_plugin import BasePlugin
from research_framework.container.container import Container
from research_framework.pipeline.wrappers import FitPredictFilterWrapper

import pandas as pd

@Container.bind(FitPredictFilterWrapper)
class Tf(BasePlugin):
    config={
        "name": "tf",
        "image":{
            "size": "w-16 h-10",
            "url": "/img/sklearn1.png",
        },
        "params": {
            "lowercase":True
        }
    }

    def fit(self, x, params:Dict[str, Any]):
        self.model = CountVectorizer(**params)
        self.model.fit(x.examples)

    def predict(self, x, *_):
        return pd.DataFrame({
            'id': x.id, 
            'text':self.model.transform(x.text), 
            'label':x.label
        })


@Container.bind(FitPredictFilterWrapper)
class TfIdf(BasePlugin):
    config={
        "name": "tf-idf",
        "image":{
            "size": "w-16 h-10",
            "url": "/img/sklearn1.png",
        },
        "params": {
            "lowercase":True
        }
    }

    def fit(self, x, params:Dict[str, Any]):
        self.model = TfidfVectorizer(**params)
        self.model.fit(x.examples)

    def predict(self, x, *_):
        return pd.DataFrame({
            'id': x.id, 
            'text':self.model.transform(x.text), 
            'label':x.label
        })

