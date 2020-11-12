

CREATE VIRTUAL TABLE search_table USING fts5(subject, body, content=messages, content_rowid=message_id);