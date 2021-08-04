import sqlite3

import numpy as np

from message import Message, STEMMER, WORDS


class DatabaseConnector:
    def __init__(self, database, pipeline, classifier):
        self._pipeline = pipeline
        self._classifier = classifier
        self._stemmer = STEMMER
        self._words = WORDS
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

    def populate_message_table(self,
                               messages,
                               labels,
                               dataset_label,
                               commit=False):

        rows = []
        for i, message in enumerate(messages):
            features = message.text_features()
            if self._pipeline is not None and self._classifier is not None:
                x = self._pipeline.transform([message])
                prob_spam = float(self._classifier.predict_proba(x)[0, 1])
            else:
                prob_spam = None
            rows.append((
                labels[i],
                dataset_label,
                features["cap_max"],
                features["cap_pct"],
                features["num_links"],
                features["has_html"],
                features["nonascii_pct"],
                prob_spam,
                message.subject_html(db_connector=self),
                message.body_html(db_connector=self),
            ), )
        self.cursor.executemany(
            "INSERT INTO messages(label, dataset, cap_max, cap_pct, num_links, has_html, " + \
                "nonascii_pct, prob_spam, subject, body) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        if commit:
            self.connection.commit()

    def get_roots(self, stems):
        all_roots = dict()
        for word in self._words:
            word_stem = self._stemmer.stem(word)
            if word_stem == "url":
                all_roots.update({"url": "url"})
                continue
            if word_stem not in all_roots or len(
                    all_roots[word_stem]) > len(word):
                all_roots.update({word_stem: word})
        stems_to_roots = dict()
        for stem in stems:
            stems_to_roots.update({stem: all_roots.get(stem, stem)})
        return stems_to_roots

    def populate_feature_table(self, messages, commit=False):
        features = []
        counter = self._pipeline.named_steps["vectorizer"].named_transformers_[
            "tdidf_body_vectorizer"].named_steps["counter"]
        coefs = self._classifier.coef_[:len(counter.get_feature_names())]
        total_counts = np.zeros(len(counter.get_feature_names()))
        for m in messages:
            counts = counter.transform([m.tokens()])
            total_counts += counts
        words = counter.get_feature_names()
        roots = self.get_roots(words)
        root_list = [roots[x] for x in words]

        for e in zip(words, root_list, coefs, np.asarray(total_counts)[0, :]):
            features.append(e)

        self.cursor.executemany(
            "INSERT INTO features (feature, root, coefficient, frequency) values (?, ?, ?, ?)",
            features)

        if commit:
            self.connection.commit()