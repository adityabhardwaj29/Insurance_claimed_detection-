-- =============================================================================
-- database/migrations/003_case_management.sql
-- Production Supabase PostgreSQL Schema - SIU Case Management, Documents & Audit
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- SUPPORTING DOCUMENTS & EVIDENCE FILES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS documents (
    document_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id                VARCHAR(24) NOT NULL REFERENCES claims(claim_id) ON DELETE CASCADE,
    document_type           VARCHAR(40) NOT NULL CHECK (document_type IN ('Claim Form', 'Invoice', 'Repair Estimate', 'Police Report', 'Identity Proof', 'Policy Copy', 'Damage Photo', 'Investigation Report', 'Other')),
    file_name               VARCHAR(255) NOT NULL,
    file_size_bytes         BIGINT,
    mime_type               VARCHAR(80),
    storage_path            VARCHAR(500) NOT NULL,
    uploaded_by             VARCHAR(120) DEFAULT 'system',
    verification_status     VARCHAR(30) DEFAULT 'Pending' CHECK (verification_status IN ('Pending', 'Verified', 'Rejected')),
    metadata                JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_claim ON documents(claim_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- INVESTIGATION CASES (SIU Triage Queue)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS investigation_cases (
    case_id                 VARCHAR(30) PRIMARY KEY,
    claim_id                VARCHAR(24) NOT NULL REFERENCES claims(claim_id) ON DELETE CASCADE,
    risk_score              DECIMAL(5,4) CHECK (risk_score >= 0 AND risk_score <= 1),
    risk_band               VARCHAR(20) CHECK (risk_band IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    priority                VARCHAR(20) NOT NULL DEFAULT 'MEDIUM' CHECK (priority IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    status                  VARCHAR(30) NOT NULL DEFAULT 'NEW' CHECK (status IN ('NEW','ASSIGNED','UNDER_REVIEW','EVIDENCE_REQUIRED','ESCALATED','RESOLVED','CLOSED','FALSE_POSITIVE')),
    assigned_to             VARCHAR(120),
    due_date                DATE,
    reason                  TEXT,
    notes                   TEXT,
    resolution              TEXT,
    final_decision          VARCHAR(30) CHECK (final_decision IN ('Approve', 'Reject', 'Manual Review', 'Fraud Suspected', 'Cleared')),
    decided_by              VARCHAR(120),
    decision_timestamp      TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cases_claim ON investigation_cases(claim_id);
CREATE INDEX IF NOT EXISTS idx_cases_status ON investigation_cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_assigned ON investigation_cases(assigned_to);

-- ─────────────────────────────────────────────────────────────────────────────
-- CASE NOTES (Investigator Log)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS case_notes (
    note_id                 SERIAL PRIMARY KEY,
    case_id                 VARCHAR(30) NOT NULL REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    author                  VARCHAR(120) NOT NULL,
    note_text               TEXT NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notes_case ON case_notes(case_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- CASE EVIDENCE
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS case_evidence (
    evidence_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id                 VARCHAR(30) NOT NULL REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    document_id             UUID REFERENCES documents(document_id) ON DELETE SET NULL,
    title                   VARCHAR(200) NOT NULL,
    evidence_type           VARCHAR(60),
    findings                TEXT,
    submitted_by            VARCHAR(120) NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evidence_case ON case_evidence(case_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- CASE EVENTS (Immutable Audit Log)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS case_events (
    event_id                SERIAL PRIMARY KEY,
    case_id                 VARCHAR(30) NOT NULL REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    event_type              VARCHAR(60) NOT NULL,
    actor                   VARCHAR(120) NOT NULL,
    old_value               VARCHAR(120),
    new_value               VARCHAR(120),
    details                 TEXT,
    timestamp               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_case ON case_events(case_id);
CREATE INDEX IF NOT EXISTS idx_events_time ON case_events(timestamp);

-- ─────────────────────────────────────────────────────────────────────────────
-- NOTIFICATIONS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    notification_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_role          VARCHAR(30) REFERENCES roles(role_id),
    recipient_email         VARCHAR(255),
    title                   VARCHAR(200) NOT NULL,
    message                 TEXT NOT NULL,
    category                VARCHAR(40) DEFAULT 'Risk Alert' CHECK (category IN ('Risk Alert', 'Case Assigned', 'Status Changed', 'Review Required', 'System')),
    link_url                VARCHAR(255),
    is_read                 BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notif_unread ON notifications(recipient_email, is_read);

-- ─────────────────────────────────────────────────────────────────────────────
-- GLOBAL AUDIT LOGS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email              VARCHAR(255) NOT NULL,
    action                  VARCHAR(80) NOT NULL,
    entity_type             VARCHAR(40) NOT NULL,
    entity_id               VARCHAR(80) NOT NULL,
    metadata                JSONB,
    ip_address              VARCHAR(45),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);

-- ─────────────────────────────────────────────────────────────────────────────
-- MODEL VERSIONS & PIPELINE PROCESSING RUNS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS model_versions (
    model_id                VARCHAR(60) PRIMARY KEY,
    model_type              VARCHAR(40) NOT NULL,
    version_tag             VARCHAR(30) NOT NULL,
    accuracy                DECIMAL(5,4),
    pr_auc                  DECIMAL(5,4),
    roc_auc                 DECIMAL(5,4),
    f1_score                DECIMAL(5,4),
    artifact_path           VARCHAR(255),
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    deployed_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO model_versions (model_id, model_type, version_tag, accuracy, pr_auc, roc_auc, f1_score, is_active)
VALUES
    ('fraud_xgboost_v1', 'Supervised Classifier', 'v1.0.0', 0.7188, 0.2348, 0.5819, 0.1818, TRUE),
    ('anomaly_iforest_v1', 'Isolation Forest + LOF', 'v1.0.0', NULL, NULL, NULL, NULL, TRUE),
    ('graph_networkx_v1', 'Knowledge Graph Topology', 'v1.0.0', NULL, NULL, NULL, NULL, TRUE),
    ('hybrid_risk_v1', 'Multi-Signal Synthesizer', 'v1.0.0', NULL, NULL, NULL, NULL, TRUE)
ON CONFLICT (model_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS processing_runs (
    run_id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id                VARCHAR(24) NOT NULL REFERENCES claims(claim_id) ON DELETE CASCADE,
    status                  VARCHAR(30) NOT NULL DEFAULT 'IN_PROGRESS' CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED')),
    current_step            VARCHAR(60),
    execution_time_ms       DOUBLE PRECISION,
    error_message           TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at            TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_runs_claim ON processing_runs(claim_id);
