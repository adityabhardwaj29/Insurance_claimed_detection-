-- =============================================================================
-- database/migrations/002_fraud_analytics.sql
-- Production Supabase PostgreSQL Schema - Machine Learning & Graph Intelligence
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- CLAIM FEATURES (Engineered Feature Store)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS claim_features (
    claim_id                VARCHAR(24) PRIMARY KEY REFERENCES claims(claim_id) ON DELETE CASCADE,
    claim_amount            DECIMAL(12,2) NOT NULL,
    claim_to_premium_ratio  DECIMAL(10,4),
    claim_to_vehicle_ratio  DECIMAL(10,4),
    claimant_age            SMALLINT,
    provider_claim_count    INTEGER DEFAULT 1,
    claimant_claim_count    INTEGER DEFAULT 1,
    vehicle_claim_count     INTEGER DEFAULT 1,
    policy_tenure_days      INTEGER,
    days_to_claim           INTEGER,
    feature_version         VARCHAR(30) NOT NULL DEFAULT 'v1.0.0',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_features_ratio ON claim_features(claim_to_premium_ratio);

-- ─────────────────────────────────────────────────────────────────────────────
-- DUPLICATE MATCHES (Pairwise Similarity Store)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS duplicate_matches (
    match_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id_1              VARCHAR(24) NOT NULL REFERENCES claims(claim_id) ON DELETE CASCADE,
    claim_id_2              VARCHAR(24) NOT NULL REFERENCES claims(claim_id) ON DELETE CASCADE,
    similarity_score        DECIMAL(5,4) NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
    duplicate_tier          VARCHAR(30) NOT NULL CHECK (duplicate_tier IN ('EXACT', 'HIGH_SIMILARITY', 'POTENTIAL_MATCH', 'LOW')),
    matched_fields          TEXT,
    similarity_breakdown    JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_claim_pair UNIQUE (claim_id_1, claim_id_2)
);

CREATE INDEX IF NOT EXISTS idx_dup_claim1 ON duplicate_matches(claim_id_1);
CREATE INDEX IF NOT EXISTS idx_dup_claim2 ON duplicate_matches(claim_id_2);
CREATE INDEX IF NOT EXISTS idx_dup_score ON duplicate_matches(similarity_score);

-- ─────────────────────────────────────────────────────────────────────────────
-- ANOMALY RESULTS (Unsupervised Isolation Forest + LOF)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS anomaly_results (
    result_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id                VARCHAR(24) NOT NULL REFERENCES claims(claim_id) ON DELETE CASCADE,
    anomaly_score           DECIMAL(5,4) NOT NULL CHECK (anomaly_score >= 0 AND anomaly_score <= 1),
    is_anomaly              BOOLEAN NOT NULL DEFAULT FALSE,
    contamination_rate      DECIMAL(4,3) DEFAULT 0.100,
    model_name              VARCHAR(60) NOT NULL DEFAULT 'IsolationForest+LOF',
    model_version           VARCHAR(30) NOT NULL DEFAULT 'v1.0.0',
    details                 JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_anomaly_claim ON anomaly_results(claim_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_score ON anomaly_results(anomaly_score);

-- ─────────────────────────────────────────────────────────────────────────────
-- FRAUD PREDICTIONS (Supervised XGBoost Classifier)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fraud_predictions (
    prediction_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id                VARCHAR(24) NOT NULL REFERENCES claims(claim_id) ON DELETE CASCADE,
    fraud_probability       DECIMAL(5,4) NOT NULL CHECK (fraud_probability >= 0 AND fraud_probability <= 1),
    fraud_prediction        SMALLINT NOT NULL CHECK (fraud_prediction IN (0, 1)),
    risk_tier               VARCHAR(20) NOT NULL CHECK (risk_tier IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    model_name              VARCHAR(60) NOT NULL DEFAULT 'XGBoostClassifier',
    model_version           VARCHAR(30) NOT NULL DEFAULT 'v1.0.0',
    feature_importance      JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pred_claim ON fraud_predictions(claim_id);
CREATE INDEX IF NOT EXISTS idx_pred_prob ON fraud_predictions(fraud_probability);

-- ─────────────────────────────────────────────────────────────────────────────
-- GRAPH INTELLIGENCE (Heterogeneous Knowledge Graph Topology)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS graph_nodes (
    node_id                 VARCHAR(60) PRIMARY KEY,
    node_type               VARCHAR(30) NOT NULL CHECK (node_type IN ('Claim','Claimant','Policy','Vehicle','Provider','Location')),
    label                   VARCHAR(120),
    degree                  INTEGER DEFAULT 0,
    fraud_neighbor_ratio    DECIMAL(5,4) DEFAULT 0.0,
    community_id            INTEGER,
    metadata                JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS graph_edges (
    edge_id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id               VARCHAR(60) NOT NULL REFERENCES graph_nodes(node_id) ON DELETE CASCADE,
    target_id               VARCHAR(60) NOT NULL REFERENCES graph_nodes(node_id) ON DELETE CASCADE,
    edge_type               VARCHAR(40) NOT NULL,
    weight                  DECIMAL(5,4) DEFAULT 1.000,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_edges_source ON graph_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON graph_edges(target_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- RISK SCORES (Phase 8: Hybrid Risk Engine Multi-Signal Blend)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS risk_scores (
    claim_id                VARCHAR(24) PRIMARY KEY REFERENCES claims(claim_id) ON DELETE CASCADE,
    fraud_probability       DECIMAL(5,4) NOT NULL CHECK (fraud_probability >= 0 AND fraud_probability <= 1),
    anomaly_score           DECIMAL(5,4) NOT NULL CHECK (anomaly_score >= 0 AND anomaly_score <= 1),
    duplicate_score         DECIMAL(5,4) NOT NULL CHECK (duplicate_score >= 0 AND duplicate_score <= 1),
    graph_risk_score        DECIMAL(5,4) NOT NULL CHECK (graph_risk_score >= 0 AND graph_risk_score <= 1),
    final_risk_score        DECIMAL(5,4) NOT NULL CHECK (final_risk_score >= 0 AND final_risk_score <= 1),
    risk_band               VARCHAR(20) NOT NULL CHECK (risk_band IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    risk_reasons            TEXT,
    scoring_version         VARCHAR(30) NOT NULL DEFAULT 'v1.0.0',
    weights_config          JSONB DEFAULT '{"fraud": 0.35, "anomaly": 0.25, "graph": 0.25, "duplicate": 0.15}'::jsonb,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_risk_final ON risk_scores(final_risk_score);
CREATE INDEX IF NOT EXISTS idx_risk_band ON risk_scores(risk_band);
