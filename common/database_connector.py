import sqlite3
from .message import Message
import mailparser

class DatabaseConnector:
    def __init__(self, database):
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
            if isinstance(message, str):
                message = Message(mailparser.parse_from_file(message))
            rows.append((labels[i], message.subject_html(db_connector=self), message.body_html(db_connector=self)))

        self.cursor.executemany(
            "INSERT INTO messages(label, subject, body) values (?, ?, ?)", rows
        )
        if commit:
            self.connection.commit()

    def populate_feature_table(self, features, commit=False):

        has_color = bool(len(features[0]) == 3)

        if has_color:
            self.cursor.executemany(
                "INSERT INTO features(feature, coefficient, color) values (?, ?, ?)",
                features,
            )
        else:
            self.cursor.executemany(
                "INSERT INTO features (feature, coefficient) values (?, ?)", features
            )
        if commit:
            self.connection.commit()
