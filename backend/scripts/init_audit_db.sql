-- ACE Veriflow — Audit trail (Phase 2)
-- Run against PostgreSQL to log who approved/rejected what and when.

CREATE TABLE IF NOT EXISTS audit_log (
    id          BIGSERIAL PRIMARY KEY,
    finding_id  TEXT      NOT NULL,
    action      TEXT      NOT NULL CHECK (action IN ('approve', 'reject')),
    user_id     TEXT      NOT NULL,
    comment     TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_finding ON audit_log (finding_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log (created_at);

-- Optional: submissions table to store verification runs
CREATE TABLE IF NOT EXISTS submissions (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name      TEXT,
    standard_id    TEXT DEFAULT 'ul-60335-1',
    overall_status TEXT,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);
