
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY,
    label TINYINT NOT NULL,
    subject TEXT NOT NULL,
    formatted_subject TEXT,
    body TEXT NOT NULL,
    fromatted_body TEXT
);

CREATE TABLE IF NOT EXISTS features (
    feature_id INTEGER PRIMARY KEY,
    feature VARCHAR(10) NOT NULL,
    coefficient FLOAT NOT NULL,
    color VARCHAR(8)
);