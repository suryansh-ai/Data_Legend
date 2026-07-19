-- Data Legend — Lakebase Schema
-- Creates tables for notes, overrides, shortlists, and review flags

CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    facility_id VARCHAR(255) NOT NULL,
    note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS overrides (
    id SERIAL PRIMARY KEY,
    facility_id VARCHAR(255) NOT NULL UNIQUE,
    original_score FLOAT,
    new_score FLOAT NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shortlists (
    id SERIAL PRIMARY KEY,
    facility_id VARCHAR(255) NOT NULL,
    list_name VARCHAR(255) DEFAULT 'default',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(facility_id, list_name)
);

CREATE TABLE IF NOT EXISTS review_flags (
    id SERIAL PRIMARY KEY,
    facility_id VARCHAR(255) NOT NULL,
    flag_type VARCHAR(100) NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_notes_facility ON notes(facility_id);
CREATE INDEX IF NOT EXISTS idx_overrides_facility ON overrides(facility_id);
CREATE INDEX IF NOT EXISTS idx_shortlists_list ON shortlists(list_name);
CREATE INDEX IF NOT EXISTS idx_flags_facility ON review_flags(facility_id);
CREATE INDEX IF NOT EXISTS idx_flags_resolved ON review_flags(resolved);
