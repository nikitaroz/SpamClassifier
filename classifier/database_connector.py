import sqlite3

from message import Message


class DatabaseConnector:
    def __init__(self, database, pipeline, classifier):
        self._pipeline = pipeline
        self._classifier = classifier
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

    def populate_message_table(self, messages, labels, commit=False):
        rows = []
        for i, message in enumerate(messages):
            if not isinstance(message, Message):
                try:
                    message = Message(message)
                except OSError:
                    continue
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
        coefs = self._classifier.coef_
        vectorizer = self._pipeline["vectorizer"].named_transformers_["tdidf_body_vectorizer"]
        for e in zip(vectorizer.get_feature_names(), coefs):
                features.append(e)

        self.cursor.executemany(
                "INSERT INTO features (feature, coefficient) values (?, ?)", features
        )
        if commit:
            self.connection.commit()
