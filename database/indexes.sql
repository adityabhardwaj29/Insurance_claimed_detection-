-- =============================================================================
-- database/indexes.sql
-- Performance indexes for the fraud detection relational schema
-- =============================================================================

-- ── CLAIMS indexes ──────────────────────────────────────────────────────────
-- FK join columns
CREATE INDEX idx_claims_claimant_id  ON claims(claimant_id);
CREATE INDEX idx_claims_policy_id    ON claims(policy_id);
CREATE INDEX idx_claims_vehicle_id   ON claims(vehicle_id);
CREATE INDEX idx_claims_provider_id  ON claims(provider_id);
CREATE INDEX idx_claims_invoice_id   ON claims(invoice_id);

-- Query filters
CREATE INDEX idx_claims_fraud_label  ON claims(fraud_label);
CREATE INDEX idx_claims_status       ON claims(status);
CREATE INDEX idx_claims_claim_type   ON claims(claim_type);
CREATE INDEX idx_claims_claim_date   ON claims(claim_date);

-- ── POLICIES indexes ────────────────────────────────────────────────────────
CREATE INDEX idx_policies_claimant_id ON policies(claimant_id);
CREATE INDEX idx_policies_policy_type ON policies(policy_type);

-- ── VEHICLES indexes ────────────────────────────────────────────────────────
CREATE INDEX idx_vehicles_claimant_id ON vehicles(claimant_id);

-- ── INVOICES indexes ────────────────────────────────────────────────────────
CREATE INDEX idx_invoices_provider_id  ON invoices(provider_id);
CREATE INDEX idx_invoices_invoice_date ON invoices(invoice_date);

-- ── PROVIDERS indexes ───────────────────────────────────────────────────────
CREATE INDEX idx_providers_city          ON providers(city);
CREATE INDEX idx_providers_provider_type ON providers(provider_type);

-- ── CLAIMANTS indexes ───────────────────────────────────────────────────────
CREATE INDEX idx_claimants_city ON claimants(city);
