DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

DROP TABLE IF EXISTS metrics;

CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    counter INTEGER
)
