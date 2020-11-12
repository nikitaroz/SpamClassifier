
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY,
    label TINYINT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    formatted_body TEXT
);

CREATE TABLE IF NOT EXISTS features (
    feature_id INTEGER PRIMARY KEY,
    feature VARCHAR(10) NOT NULL,
    coefficient FLOAT NOT NULL,
    color VARCHAR(8)
);

-- Create an external content fts5 table to index messages.
CREATE VIRTUAL TABLE IF NOT EXISTS fts_idx USING fts5 (
    subject, 
    body, 
    content='messages', 
    content_rowid='message_id'
);

-- Triggers to keep the FTS index up to date.
CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
  INSERT INTO fts_idx(rowid, subject, body) VALUES (new.message_id, new.subject, new.body);
END;
CREATE TRIGGER messages_ad AFTER DELETE ON messages BEGIN
  INSERT INTO fts_idx(fts_idx, rowid, subject, body) VALUES('delete', old.message_id, old.subject, old.body);
END;
CREATE TRIGGER messages_au AFTER UPDATE ON messages BEGIN
  INSERT INTO fts_idx(fts_idx, rowid, subject, body) VALUES('delete', old.message_id, old.subject, old.body);
  INSERT INTO fts_idx(rowid, subject, body) VALUES (new.message_id, new.subject, new.body);
END;