-- roostsocial.art schema
CREATE TABLE IF NOT EXISTS users (
  username TEXT PRIMARY KEY,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS claims (
  token TEXT PRIMARY KEY,
  username TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY,
  username TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS chirps (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  message TEXT DEFAULT '',
  image_key TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS chirp_tags (
  chirp_id INTEGER NOT NULL,
  tag TEXT NOT NULL,
  added_by TEXT NOT NULL,
  UNIQUE(chirp_id, tag, added_by)
);
CREATE TABLE IF NOT EXISTS ratings (
  chirp_id INTEGER NOT NULL,
  username TEXT NOT NULL,
  score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 10),
  PRIMARY KEY (chirp_id, username)
);
CREATE INDEX IF NOT EXISTS idx_chirps_created ON chirps(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tags_chirp ON chirp_tags(chirp_id);
CREATE INDEX IF NOT EXISTS idx_ratings_chirp ON ratings(chirp_id);
