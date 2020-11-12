import sqlite3

class DatabasePopulator:
    def __init__(self, database):
        self.database = database

    def populate_schema(self, schema):
        conn = sqlite3.connect(self.database)
        conn.executescript(open(schema).read())
        conn.commit()
        conn.close()


    def populate_message_table(self, messages, labels):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        rows = []
        for i, message in enumerate(messages):
            rows.append((labels[i], message.subject_text, message.body_text))

        cursor.executemany("INSERT INTO messages(label, subject, body) values (?, ?, ?)", rows)
        conn.commit()
        conn.close()


    def populate_feature_table(self, features):

        has_color = bool(len(features[0]) == 3)

        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        if has_color:
            cursor.executemany("INSERT INTO features(feature, coefficient, color) values (?, ?, ?)", features)
        else:
            cursor.executemany("INSERT INTO features (feature, coefficient) values (?, ?)", features)
        conn.commit()
        conn.close()
