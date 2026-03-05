-- Core schema scaffold for Goal Tactics.

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_bot BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clubs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    money BIGINT NOT NULL DEFAULT 5000000,
    stars BIGINT NOT NULL DEFAULT 20000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS players (
    id BIGSERIAL PRIMARY KEY,
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    name TEXT NOT NULL,
    age SMALLINT NOT NULL CHECK (age BETWEEN 16 AND 34),
    strength NUMERIC(6,2) NOT NULL CHECK (strength >= 0 AND strength <= 1000),
    talent SMALLINT NOT NULL CHECK (talent BETWEEN 1 AND 10),
    position TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS matches (
    id BIGSERIAL PRIMARY KEY,
    competition TEXT NOT NULL,
    season_id BIGINT NOT NULL,
    home_club_id BIGINT NOT NULL REFERENCES clubs(id),
    away_club_id BIGINT NOT NULL REFERENCES clubs(id),
    status TEXT NOT NULL,
    lock_at TIMESTAMPTZ NOT NULL,
    kickoff_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS training_logs (
    id BIGSERIAL,
    player_id BIGINT NOT NULL REFERENCES players(id),
    run_at TIMESTAMPTZ NOT NULL,
    gain NUMERIC(6,4) NOT NULL,
    decay NUMERIC(6,4) NOT NULL DEFAULT 0,
    fatigue NUMERIC(6,2) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS economy_transactions (
    id BIGSERIAL,
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    currency TEXT NOT NULL,
    amount BIGINT NOT NULL,
    reason TEXT NOT NULL,
    idempotency_key TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE INDEX IF NOT EXISTS idx_players_club_id ON players(club_id);
CREATE INDEX IF NOT EXISTS idx_matches_kickoff_at ON matches(kickoff_at);
CREATE INDEX IF NOT EXISTS idx_econ_created_at ON economy_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_training_created_at ON training_logs(created_at);
