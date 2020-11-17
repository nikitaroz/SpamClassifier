import mailparser
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from .message import Message


class MessageTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, input="message"):
        """string {‘filename’, ‘file’, ‘content’}, """
        self.input = input
        self.messages = []

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """X is a list of files"""
        feature_aggregator = []
        if isinstance(X, str):
            raise ValueError("Must be a list or iterable, not a string")
        for x in X:
            if self.input == "content":
                mailparser_obj = mailparser.parse_from_string(x)
            elif self.input == "file":
                mailparser_obj = mailparser.parse_from_file_obj(x)
            elif self.input == "filename":
                mailparser_obj = mailparser.parse_from_file(x)
            elif self.input == "message":
                feature_aggregator.append((x.tokens(),))
                continue
            else:
                raise ValueError("Input must be: file, filename, or message")
            feature_aggregator.append((Message(mailparser_obj).tokens(),))

        return pd.DataFrame.from_records(feature_aggregator, columns=("tokens",))
