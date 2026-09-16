-- =============================================================================
-- database/views.sql
-- Analytical views derived from the relational schema
-- All views compute from actual data — no hardcoded values.
-- =============================================================================

-- ── claim_risk_base ──────────────────────────────────────────────────────────
-- Minimal claim-level view for risk scoring pipeline.
-- Includes key identifiers, amounts, status, and fraud label.
CREATE OR REPLACE VIEW claim_risk_base AS
SELECT
    c.claim_id,
    c.claimant_id,
    c.policy_id,
    c.vehicle_id,
    c.provider_id,
    c.invoice_id,
    c.claim_date,
    c.claim_amount,
    c.claim_type,
    c.status,
    c.fraud_label,
    -- Policy context
    p.policy_type,
    p.premium,
    p.start_date          AS policy_start,
    p.end_date            AS policy_end,
    p.date_order_invalid,
    -- Provider context
    pr.provider_type,
    pr.rating             AS provider_rating,
    -- Invoice context
    i.invoice_amount,
    i.invoice_date,
    -- Claimant context
    cl.age                AS claimant_age,
    cl.city               AS claimant_city,
    cl.gender,
    cl.marital_status
FROM claims c
JOIN policies  p  ON c.policy_id   = p.policy_id
JOIN providers pr ON c.provider_id = pr.provider_id
JOIN invoices  i  ON c.invoice_id  = i.invoice_id
JOIN claimants cl ON c.claimant_id = cl.claimant_id;

COMMENT ON VIEW claim_risk_base IS
    'Denormalized claim view for the fraud scoring pipeline. '
    'Joins all dimension tables. Source: relational schema.';


-- ── provider_summary ─────────────────────────────────────────────────────────
-- Per-provider claim statistics (computed from actual claims).
CREATE OR REPLACE VIEW provider_summary AS
SELECT
    p.provider_id,
    p.provider_name,
    p.provider_type,
    p.city,
    p.rating,
    COUNT(c.claim_id)                                   AS total_claims,
    COUNT(DISTINCT c.claimant_id)                       AS unique_claimants,
    SUM(c.claim_amount)                                 AS total_claim_amount,
    AVG(c.claim_amount)                                 AS avg_claim_amount,
    SUM(CASE WHEN c.fraud_label = 1 THEN 1 ELSE 0 END) AS fraud_claims,
    CASE
        WHEN COUNT(c.claim_id) > 0
        THEN ROUND(
            100.0 * SUM(CASE WHEN c.fraud_label = 1 THEN 1 ELSE 0 END)
            / COUNT(c.claim_id), 2)
        ELSE 0
    END                                                 AS fraud_rate_pct
FROM providers p
LEFT JOIN claims c ON p.provider_id = c.provider_id
GROUP BY p.provider_id, p.provider_name, p.provider_type, p.city, p.rating;

COMMENT ON VIEW provider_summary IS
    'Aggregate claim counts and fraud rate per provider. Computed from actual claim data.';


-- ── claimant_summary ─────────────────────────────────────────────────────────
-- Per-claimant claim history (computed from actual claims).
CREATE OR REPLACE VIEW claimant_summary AS
SELECT
    cl.claimant_id,
    cl.name,
    cl.age,
    cl.city,
    cl.gender,
    cl.marital_status,
    COUNT(c.claim_id)                                   AS total_claims,
    SUM(c.claim_amount)                                 AS total_claim_amount,
    AVG(c.claim_amount)                                 AS avg_claim_amount,
    MAX(c.claim_date)                                   AS latest_claim_date,
    MIN(c.claim_date)                                   AS earliest_claim_date,
    SUM(CASE WHEN c.fraud_label = 1 THEN 1 ELSE 0 END) AS fraud_claims,
    COUNT(DISTINCT c.policy_id)                         AS policies_used,
    COUNT(DISTINCT c.provider_id)                       AS providers_used
FROM claimants cl
LEFT JOIN claims c ON cl.claimant_id = c.claimant_id
GROUP BY cl.claimant_id, cl.name, cl.age, cl.city, cl.gender, cl.marital_status;

COMMENT ON VIEW claimant_summary IS
    'Aggregate claim history per claimant. Computed from actual claim data.';


-- ── fraud_overview ───────────────────────────────────────────────────────────
-- Dataset-level fraud statistics (no hardcoded values).
CREATE OR REPLACE VIEW fraud_overview AS
SELECT
    COUNT(*)                                                   AS total_claims,
    SUM(CASE WHEN fraud_label = 1 THEN 1 ELSE 0 END)          AS fraud_count,
    SUM(CASE WHEN fraud_label = 0 THEN 1 ELSE 0 END)          AS legit_count,
    ROUND(100.0 * SUM(CASE WHEN fraud_label = 1 THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                       AS fraud_rate_pct,
    SUM(CASE WHEN fraud_label = 1 THEN claim_amount ELSE 0 END) AS fraud_amount_total,
    AVG(CASE WHEN fraud_label = 1 THEN claim_amount END)       AS avg_fraud_amount,
    AVG(CASE WHEN fraud_label = 0 THEN claim_amount END)       AS avg_legit_amount
FROM claims;

COMMENT ON VIEW fraud_overview IS
    'Dataset-level fraud statistics. All values computed from actual claims table.';


-- ── invoice_reuse ─────────────────────────────────────────────────────────────
-- Identify invoices referenced by more than one claim (potential fraud signal).
CREATE OR REPLACE VIEW invoice_reuse AS
SELECT
    i.invoice_id,
    i.provider_id,
    i.invoice_amount,
    i.invoice_date,
    COUNT(c.claim_id)                                   AS claim_count,
    SUM(CASE WHEN c.fraud_label = 1 THEN 1 ELSE 0 END) AS fraud_claim_count
FROM invoices i
JOIN claims c ON i.invoice_id = c.invoice_id
GROUP BY i.invoice_id, i.provider_id, i.invoice_amount, i.invoice_date
HAVING COUNT(c.claim_id) > 1
ORDER BY claim_count DESC;

COMMENT ON VIEW invoice_reuse IS
    'Invoices referenced by more than one claim. '
    'Potential fraud signal. Source-data characteristic, not an error.';
