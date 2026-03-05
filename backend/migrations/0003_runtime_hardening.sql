-- Runtime hardening additions for auth sessions and deterministic settlement audit.

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);

CREATE TABLE IF NOT EXISTS match_settlements (
    id BIGSERIAL PRIMARY KEY,
    fixture_id BIGINT NOT NULL,
    competition TEXT NOT NULL,
    season_id BIGINT NOT NULL,
    home_club_id BIGINT,
    away_club_id BIGINT,
    home_goals INTEGER,
    away_goals INTEGER,
    source TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_match_settlements_fixture ON match_settlements(fixture_id);
CREATE INDEX IF NOT EXISTS idx_match_settlements_created ON match_settlements(created_at);
