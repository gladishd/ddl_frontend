-- file: create_document_features.sql
BEGIN;

CREATE TABLE IF NOT EXISTS documents (
  id          SERIAL PRIMARY KEY,
  title       TEXT NOT NULL,
  description TEXT,
  image       TEXT,
  href        TEXT NOT NULL UNIQUE
);

-- likes start at 10
CREATE TABLE IF NOT EXISTS document_likes (
  document_id INT PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
  count       INT NOT NULL DEFAULT 10
);

-- views start at 20
CREATE TABLE IF NOT EXISTS document_views (
  document_id INT PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
  count       INT NOT NULL DEFAULT 20
);

CREATE TABLE IF NOT EXISTS document_tags (
  document_id INT REFERENCES documents(id) ON DELETE CASCADE,
  tag         TEXT NOT NULL,
  PRIMARY KEY (document_id, tag)
);

COMMIT;
