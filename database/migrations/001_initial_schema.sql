-- =============================================================================
-- database/migrations/001_initial_schema.sql
-- Production Supabase PostgreSQL Schema - Core Domain Entities
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- ROLES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS roles (
    role_id         VARCHAR(30) PRIMARY KEY,
    role_name       VARCHAR(60) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO roles (role_id, role_name, description)
VALUES 
    ('ADMIN', 'Administrator', 'Full system configuration, user management, and audit logs'),
    ('CLAIMS_OFFICER', 'Claims Officer', 'Create, edit, view, and submit claims for fraud analysis'),
    ('INVESTIGATOR', 'SIU Investigator', 'Investigate flagged claims, manage evidence, add notes, and record findings'),
    ('SUPERVISOR', 'Claims Supervisor', 'Review investigations, approve/reject decisions, and monitor triage queue'),
    ('ANALYST', 'Risk & Fraud Analyst', 'Inspect analytics, model evaluation metrics, and system monitoring')
ON CONFLICT (role_id) DO NOTHING;

-- ─────────────────────────────────────────────────────────────────────────────
-- USER PROFILES (Integrated with Supabase Auth or local authentication)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    full_name       VARCHAR(120) NOT NULL,
    role_id         VARCHAR(30) NOT NULL REFERENCES roles(role_id) DEFAULT 'CLAIMS_OFFICER',
    department      VARCHAR(80) DEFAULT 'Claims & Fraud Operations',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed default administrative and demo users
INSERT INTO profiles (email, full_name, role_id, department)
VALUES 
    ('admin@insurance.com', 'System Administrator', 'ADMIN', 'IT & Security'),
    ('claims.officer@insurance.com', 'Priya Sharma', 'CLAIMS_OFFICER', 'Claim Intake'),
    ('investigator@insurance.com', 'Rahul Varma', 'INVESTIGATOR', 'Special Investigation Unit'),
    ('supervisor@insurance.com', 'Ananya Deshmukh', 'SUPERVISOR', 'SIU Management'),
    ('analyst@insurance.com', 'Vikram Malhotra', 'ANALYST', 'Data Science & Risk Analytics')
ON CONFLICT (email) DO NOTHING;

-- ─────────────────────────────────────────────────────────────────────────────
-- CLAIMANTS / CUSTOMERS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS claimants (
    claimant_id     VARCHAR(20)  NOT NULL PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    age             SMALLINT,
    city            VARCHAR(60),
    gender          CHAR(1)      CHECK (gender IN ('M', 'F', 'O')),
    marital_status  VARCHAR(20),
    phone           VARCHAR(30),
    email           VARCHAR(120),
    address         TEXT,
    occupation      VARCHAR(80),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_claimants_name ON claimants(name);
CREATE INDEX IF NOT EXISTS idx_claimants_city ON claimants(city);

-- ─────────────────────────────────────────────────────────────────────────────
-- PROVIDERS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS providers (
    provider_id     VARCHAR(20)  NOT NULL PRIMARY KEY,
    provider_name   VARCHAR(120) NOT NULL,
    city            VARCHAR(60),
    provider_type   VARCHAR(30)  CHECK (provider_type IN ('Surveyor','Dealer','Garage','Hospital','Other')),
    rating          DECIMAL(3,1) CHECK (rating >= 0 AND rating <= 5),
    phone           VARCHAR(30),
    address         TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_providers_type ON providers(provider_type);
CREATE INDEX IF NOT EXISTS idx_providers_city ON providers(city);

-- ─────────────────────────────────────────────────────────────────────────────
-- POLICIES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS policies (
    policy_id           VARCHAR(20)   NOT NULL PRIMARY KEY,
    claimant_id         VARCHAR(20)   NOT NULL REFERENCES claimants(claimant_id) ON DELETE RESTRICT,
    start_date          DATE,
    end_date            DATE,
    policy_type         VARCHAR(30)   CHECK (policy_type IN ('Comprehensive','Zero Dep','Third Party','Health','Property')),
    premium             DECIMAL(12,2) CHECK (premium >= 0),
    coverage_amount     DECIMAL(12,2) DEFAULT 500000.00,
    deductible          DECIMAL(12,2) DEFAULT 2000.00,
    status              VARCHAR(20)   DEFAULT 'Active' CHECK (status IN ('Active', 'Expired', 'Suspended', 'Cancelled')),
    date_order_invalid  BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_policies_claimant ON policies(claimant_id);
CREATE INDEX IF NOT EXISTS idx_policies_status ON policies(status);

-- ─────────────────────────────────────────────────────────────────────────────
-- VEHICLES / ASSETS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id       VARCHAR(20)  NOT NULL PRIMARY KEY,
    claimant_id      VARCHAR(20)  NOT NULL REFERENCES claimants(claimant_id) ON DELETE RESTRICT,
    make             VARCHAR(40),
    vehicle_type     VARCHAR(30),
    registration_no  VARCHAR(30),
    model_year       SMALLINT     CHECK (model_year >= 1990 AND model_year <= 2030),
    vin              VARCHAR(40),
    vehicle_value    DECIMAL(12,2),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vehicles_claimant ON vehicles(claimant_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_reg ON vehicles(registration_no);

-- ─────────────────────────────────────────────────────────────────────────────
-- INVOICES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id      VARCHAR(24)   NOT NULL PRIMARY KEY,
    provider_id     VARCHAR(20)   NOT NULL REFERENCES providers(provider_id) ON DELETE RESTRICT,
    invoice_amount  DECIMAL(12,2) CHECK (invoice_amount >= 0),
    invoice_date    DATE,
    service_type    VARCHAR(60),
    description     TEXT,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoices_provider ON invoices(provider_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- CLAIMS (Central Fact Table)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS claims (
    claim_id            VARCHAR(24)   NOT NULL PRIMARY KEY,
    claimant_id         VARCHAR(20)   NOT NULL REFERENCES claimants(claimant_id) ON DELETE RESTRICT,
    policy_id           VARCHAR(20)   NOT NULL REFERENCES policies(policy_id) ON DELETE RESTRICT,
    vehicle_id          VARCHAR(20)   NOT NULL REFERENCES vehicles(vehicle_id) ON DELETE RESTRICT,
    provider_id         VARCHAR(20)   NOT NULL REFERENCES providers(provider_id) ON DELETE RESTRICT,
    invoice_id          VARCHAR(24)   NOT NULL REFERENCES invoices(invoice_id) ON DELETE RESTRICT,
    claim_date          DATE          NOT NULL,
    claim_amount        DECIMAL(12,2) NOT NULL CHECK (claim_amount > 0),
    claim_type          VARCHAR(40)   NOT NULL CHECK (claim_type IN ('Theft','Glass Damage','Fire','Accident','Natural Disaster','Other')),
    status              VARCHAR(30)   NOT NULL DEFAULT 'Submitted' CHECK (status IN ('Draft', 'Submitted', 'Validating', 'Processing', 'Analyzed', 'Manual Review', 'Under Review', 'Approved', 'Rejected', 'Closed', 'Error')),
    fraud_label         SMALLINT      CHECK (fraud_label IN (0, 1)),
    description         TEXT,
    incident_time       TIME,
    incident_location   VARCHAR(120),
    police_report       BOOLEAN       DEFAULT FALSE,
    severity            VARCHAR(20)   DEFAULT 'Medium' CHECK (severity IN ('Low', 'Medium', 'High', 'Total Loss')),
    assigned_to         VARCHAR(80),
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_claims_claimant ON claims(claimant_id);
CREATE INDEX IF NOT EXISTS idx_claims_policy ON claims(policy_id);
CREATE INDEX IF NOT EXISTS idx_claims_provider ON claims(provider_id);
CREATE INDEX IF NOT EXISTS idx_claims_date ON claims(claim_date);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
CREATE INDEX IF NOT EXISTS idx_claims_fraud_label ON claims(fraud_label);

-- ─────────────────────────────────────────────────────────────────────────────
-- LOCATIONS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS locations (
    location_id  VARCHAR(20)   NOT NULL PRIMARY KEY,
    city         VARCHAR(60)   NOT NULL,
    latitude     DECIMAL(9,6),
    longitude    DECIMAL(9,6),
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_locations_city ON locations(city);
