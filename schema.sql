
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY,
    label TINYINT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tokens (
    token_id INTEGER PRIMARY KEY,
    message_id INTEGER NOT NULL,
    section SMALLINT NOT NULL,
    start_position INTEGER NOT NULL,
    end_position INTEGER NOT NULL,
    coefficient FLOAT NOT NULL,
    FOREIGN KEY(message_id) REFERENCES messages (message_id)
);

CREATE TABLE IF NOT EXISTS features (
    feature_id INTEGER PRIMARY KEY,
    feature VARCHAR(10) NOT NULL,
    coefficient FLOAT NOT NULL
);