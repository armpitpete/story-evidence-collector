-- MP evidence cache schema
-- This schema is for the private server database, not for GitHub data storage.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
  source_id TEXT PRIMARY KEY,
  source_system TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_url TEXT,
  source_path TEXT,
  licence_note TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS imports (
  import_run_id TEXT PRIMARY KEY,
  source_id TEXT,
  importer_name TEXT NOT NULL,
  importer_version TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  dry_run INTEGER NOT NULL DEFAULT 1,
  network_access_used INTEGER NOT NULL DEFAULT 0,
  input_path TEXT,
  output_path TEXT,
  rows_read INTEGER NOT NULL DEFAULT 0,
  rows_written INTEGER NOT NULL DEFAULT 0,
  warning_count INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  FOREIGN KEY (source_id) REFERENCES sources(source_id)
);

CREATE TABLE IF NOT EXISTS members (
  member_key TEXT PRIMARY KEY,
  source_system TEXT NOT NULL,
  source_member_id TEXT,
  display_name TEXT NOT NULL,
  party_name TEXT,
  constituency_name TEXT,
  start_date TEXT,
  end_date TEXT,
  source_trace TEXT,
  import_run_id TEXT,
  FOREIGN KEY (import_run_id) REFERENCES imports(import_run_id)
);

CREATE TABLE IF NOT EXISTS divisions (
  division_key TEXT PRIMARY KEY,
  source_system TEXT NOT NULL,
  division_id TEXT NOT NULL,
  division_date TEXT NOT NULL,
  division_title TEXT,
  house TEXT,
  source_url TEXT,
  source_path TEXT,
  source_trace TEXT,
  import_run_id TEXT,
  FOREIGN KEY (import_run_id) REFERENCES imports(import_run_id)
);

CREATE TABLE IF NOT EXISTS member_votes (
  vote_key TEXT PRIMARY KEY,
  source_system TEXT NOT NULL,
  division_key TEXT NOT NULL,
  member_key TEXT,
  target_mp TEXT NOT NULL,
  recorded_vote TEXT,
  vote_side TEXT,
  meaning_quality TEXT NOT NULL DEFAULT 'needs_review',
  source_url TEXT,
  source_path TEXT,
  source_trace TEXT,
  import_run_id TEXT,
  FOREIGN KEY (division_key) REFERENCES divisions(division_key),
  FOREIGN KEY (member_key) REFERENCES members(member_key),
  FOREIGN KEY (import_run_id) REFERENCES imports(import_run_id)
);

CREATE TABLE IF NOT EXISTS coverage (
  coverage_key TEXT PRIMARY KEY,
  source_system TEXT NOT NULL,
  scope_name TEXT NOT NULL,
  date_from TEXT,
  date_to TEXT,
  rows_available INTEGER NOT NULL DEFAULT 0,
  rows_imported INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  notes TEXT,
  import_run_id TEXT,
  FOREIGN KEY (import_run_id) REFERENCES imports(import_run_id)
);

CREATE TABLE IF NOT EXISTS validation_messages (
  message_id INTEGER PRIMARY KEY AUTOINCREMENT,
  import_run_id TEXT,
  severity TEXT NOT NULL,
  message_code TEXT NOT NULL,
  message TEXT NOT NULL,
  related_path TEXT,
  related_key TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (import_run_id) REFERENCES imports(import_run_id)
);

CREATE INDEX IF NOT EXISTS idx_member_votes_source_division_mp
  ON member_votes(source_system, division_key, target_mp);

CREATE INDEX IF NOT EXISTS idx_divisions_date
  ON divisions(division_date);

CREATE INDEX IF NOT EXISTS idx_imports_status
  ON imports(status);

CREATE INDEX IF NOT EXISTS idx_validation_import
  ON validation_messages(import_run_id, severity);
