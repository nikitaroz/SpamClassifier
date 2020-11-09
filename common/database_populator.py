import sqlite3

class DatabasePopulator:
    def __init__(self, database):
        self.database = database


    def populate_message_table(self, messages):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        rows = []
        for message in messages:
            rows.append((message.label, message.subject_text, message.body_text))

        cursor.executemany("INSERT INTO messages(label, subject, body) values (?, ?, ?)", rows)
        conn.commit()
        conn.close()


    def populate_token_table(self, tokens):
        #conn = sqlite3.connect(self.database)
        #cursor = conn.cursor()
        #rows = []
        #for token in tokens:
        #    rows.append((token.))
        raise NotImplementedError

