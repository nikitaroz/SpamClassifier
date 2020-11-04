import sqlite3

class DatabasePopulator:
    def __init__(self, database):
        self.database = database

    def populate_message_table(self, messages):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        rows = []
        for message in messages:
            rows.append((message.label, message.text))

        cursor.executemany("INSERT INTO messages(label, text) values (?, ?)", rows)
        conn.commit()
        conn.close()

    def populate_active_token_table(self):
        raise NotImplementedError

