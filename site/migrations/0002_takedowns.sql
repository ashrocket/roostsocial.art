-- Art deletion requests: owners remove instantly; anyone logged-in can flag
-- offensive art, which hides it pending review.
ALTER TABLE chirps ADD COLUMN status TEXT NOT NULL DEFAULT 'live';
CREATE TABLE IF NOT EXISTS takedowns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chirp_id INTEGER NOT NULL,
  requester TEXT NOT NULL,
  reason TEXT NOT NULL CHECK(reason IN ('owner','offensive')),
  note TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_takedowns_status ON takedowns(status);
