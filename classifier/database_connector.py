import sqlite3

import numpy as np

from message import Message

class DatabaseConnector:
    def __init__(self, database, pipeline, classifier, messages):
        self._pipeline = pipeline
        self._classifier = classifier
        self._messages = messages
        for i, m in enumerate(self._messages):
            if not isinstance(m, Message):
                self._messages[i] = Message(m)
        self._conn = sqlite3.connect(database, check_same_thread=False)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def populate_schema(self, schema):
        self.connection.executescript(open(schema).read())

    def populate_message_table(self, labels, commit=False):
        rows = []
        for i, message in enumerate(self._messages):
            features = message.text_features()
            if self._pipeline is not None and self._classifier is not None:
                x = self._pipeline.transform([message])
                prob_spam = float(self._classifier.predict_proba(x)[0, 1])
            else:
                prob_spam = None
            rows.append(
                (
                    labels[i],
                    features["cap_max"],
                    features["cap_pct"],
                    features["num_links"],
                    features["has_html"],
                    features["nonascii_pct"],
                    prob_spam,
                    message.subject_html(db_connector=self),
                    message.body_html(db_connector=self),
                ),
            )
        self.cursor.executemany(
            "INSERT INTO messages(label, cap_max, cap_pct, num_links, has_html, " + \
                "nonascii_pct, prob_spam, subject, body) values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        if commit:
            self.connection.commit()

    def populate_feature_table(self, commit=False):
        features = []
        counter = self._pipeline.named_steps["vectorizer"].named_transformers_["tdidf_body_vectorizer"].named_steps["counter"]
        coefs = self._classifier.coef_[:len(counter.get_feature_names())]
        total_counts = np.zeros(len(counter.get_feature_names()))
        for m in self._messages:
            counts = counter.transform([m.tokens()])
            total_counts += counts
        for e in zip(counter.get_feature_names(), coefs, np.asarray(total_counts)[0, :]):
            features.append(e)
        self.cursor.executemany(
            "INSERT INTO features (feature, coefficient, frequency) values (?, ?, ?)", features
        )
        if commit:
            self.connection.commit()