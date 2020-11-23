import mailparser
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from .message import Message


class MessageTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        """string {‘filename’, ‘file’, ‘content’}, """
        self.messages = []

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """X is a list of files"""
        feature_aggregator = []
        if isinstance(X, str):
            raise ValueError("Must be a list or iterable, not a string")
        
        for x in X:
            if isinstance(x, Message):
                message = x
            else:
                try:
                    message = Message(x)
                except OSError:
                    print(f"had an error on {x}. Replacing with empty.")
                    message = Message(" ")
                    
            feature_aggregator.append({**{"tokens": message.tokens()}, **message.text_features()})

        return pd.DataFrame.from_records(feature_aggregator) 
