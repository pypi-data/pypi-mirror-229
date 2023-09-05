from abc import ABC, abstractmethod


class BasePlugin(ABC):
    @abstractmethod
    def fit(*args, **kwargs): ...
    
    @abstractmethod
    def predict(*args, **kwargs): ...