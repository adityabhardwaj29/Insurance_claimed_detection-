-- =============================================================================
-- database/schema.sql
-- Graph-Enhanced Insurance Claim Fraud Detection
-- Normalised relational schema (PostgreSQL / SQLite compatible)
-- =============================================================================
-- Source data is SYNTHETIC (project-generated demo data, not real insurance).
-- Schema reflects the 7-entity relational model derived from:
--   data/master/insurance_claim_dataset.xlsx  (source)
--   data/processed/                           (cleaned)
--   data/relational/                          (relational layer)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Drop order (reverse FK dependency)
-- ─────────────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS policies;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS providers;
DROP TABLE IF EXISTS claimants;
DROP TABLE IF EXISTS locations;

-- ─────────────────────────────────────────────────────────────────────────────
-- CLAIMANTS
-- Source: data/relational/claimants.csv
-- Natural PK: claimant_id (CLT0001 – CLT0120, sequential, no gaps observed)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE claimants (
    claimant_id     VARCHAR(10)  NOT NULL PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    age             SMALLINT,                       -- nullable: invalid ages flagged NA
    city            VARCHAR(40),                    -- nullable: unknown city → NA
    gender          CHAR(1)      CHECK (gender IN ('M', 'F')),
    marital_status  VARCHAR(10)  CHECK (marital_status IN ('Married', 'Single'))
);

COMMENT ON TABLE  claimants              IS 'Insurance claimants. Data is synthetic (project-generated).';
COMMENT ON COLUMN claimants.claimant_id IS 'Primary key. Format: CLT followed by 4 digits.';
COMMENT ON COLUMN claimants.age         IS 'Age in years. Valid range 18–100. NULL if originally invalid.';
COMMENT ON COLUMN claimants.gender      IS 'M = Male, F = Female.';

-- ─────────────────────────────────────────────────────────────────────────────
-- PROVIDERS
-- Source: data/relational/providers.csv
-- Natural PK: provider_id (PRV001 – PRV025)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE providers (
    provider_id     VARCHAR(10)  NOT NULL PRIMARY KEY,
    provider_name   VARCHAR(120) NOT NULL,
    city            VARCHAR(40),
    provider_type   VARCHAR(20)  CHECK (provider_type IN ('Surveyor','Dealer','Garage','Hospital')),
    rating          DECIMAL(3,1) CHECK (rating >= 0 AND rating <= 5)
);

COMMENT ON TABLE  providers              IS 'Service providers (surveyors, dealers, garages, hospitals).';
COMMENT ON COLUMN providers.provider_id IS 'Primary key. Format: PRV followed by 3 digits.';
COMMENT ON COLUMN providers.rating      IS 'Provider quality rating. Range 0.0–5.0.';

-- ─────────────────────────────────────────────────────────────────────────────
-- POLICIES
-- Source: data/relational/policies.csv
-- Natural PK: policy_id (POL0001 – POL0140)
-- FK: claimant_id → claimants.claimant_id
-- NOTE: 4 rows have end_date <= start_date (data quality issue in source).
--       These are retained for FK integrity. date_order_invalid flag is set.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE policies (
    policy_id           VARCHAR(10)  NOT NULL PRIMARY KEY,
    claimant_id         VARCHAR(10)  NOT NULL REFERENCES claimants(claimant_id),
    start_date          DATE,
    end_date            DATE,
    policy_type         VARCHAR(20)  CHECK (policy_type IN ('Comprehensive','Zero Dep','Third Party')),
    premium             DECIMAL(12,2) CHECK (premium > 0),
    date_order_invalid  BOOLEAN      NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE  policies                         IS 'Insurance policies held by claimants.';
COMMENT ON COLUMN policies.policy_id              IS 'Primary key. Format: POL followed by 4 digits.';
COMMENT ON COLUMN policies.date_order_invalid     IS
    'TRUE for the 4 policies where end_date <= start_date in source data. '
    'Rows are retained for FK integrity. Flagged for investigation.';

-- ─────────────────────────────────────────────────────────────────────────────
-- VEHICLES
-- Source: data/relational/vehicles.csv
-- Natural PK: vehicle_id (VEH0001 – VEH0130)
-- FK: claimant_id → claimants.claimant_id
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE vehicles (
    vehicle_id       VARCHAR(10)  NOT NULL PRIMARY KEY,
    claimant_id      VARCHAR(10)  NOT NULL REFERENCES claimants(claimant_id),
    make             VARCHAR(20)  CHECK (make IN ('Tata','Maruti','Hyundai','Mahindra','Honda')),
    vehicle_type     VARCHAR(20)  CHECK (vehicle_type IN ('MUV','Sedan','Hatchback','SUV')),
    registration_no  VARCHAR(20),
    model_year       SMALLINT     CHECK (model_year >= 1990 AND model_year <= 2026)
);

COMMENT ON TABLE  vehicles                  IS 'Vehicles owned by claimants.';
COMMENT ON COLUMN vehicles.vehicle_id      IS 'Primary key. Format: VEH followed by 4 digits.';
COMMENT ON COLUMN vehicles.registration_no IS 'All plates are MH-prefix (Maharashtra). Synthetic.';

-- ─────────────────────────────────────────────────────────────────────────────
-- INVOICES
-- Source: data/relational/invoices.csv
-- Natural PK: invoice_id (INV00001 – INV00220)
-- FK: provider_id → providers.provider_id
-- NOTE: invoice_ids are not 1:1 with claims. Multiple claims may reference
--       the same invoice_id. This is a source-data characteristic.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE invoices (
    invoice_id      VARCHAR(12)   NOT NULL PRIMARY KEY,
    provider_id     VARCHAR(10)   NOT NULL REFERENCES providers(provider_id),
    invoice_amount  DECIMAL(12,2) CHECK (invoice_amount > 0),
    invoice_date    DATE,
    description     TEXT
);

COMMENT ON TABLE  invoices                   IS 'Service invoices issued by providers.';
COMMENT ON COLUMN invoices.invoice_id       IS 'Primary key. Format: INV followed by 5 digits.';
COMMENT ON COLUMN invoices.invoice_amount   IS 'Invoice value in INR.';

-- ─────────────────────────────────────────────────────────────────────────────
-- CLAIMS  (central fact table)
-- Source: data/relational/claims.csv
-- Natural PK: claim_id (CLM00001 – CLM00320)
-- FKs: claimant_id, policy_id, vehicle_id, provider_id, invoice_id
-- fraud_label: 0 = legitimate, 1 = fraud. SYNTHETIC ground truth.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE claims (
    claim_id      VARCHAR(12)   NOT NULL PRIMARY KEY,
    claimant_id   VARCHAR(10)   NOT NULL REFERENCES claimants(claimant_id),
    policy_id     VARCHAR(10)   NOT NULL REFERENCES policies(policy_id),
    vehicle_id    VARCHAR(10)   NOT NULL REFERENCES vehicles(vehicle_id),
    provider_id   VARCHAR(10)   NOT NULL REFERENCES providers(provider_id),
    invoice_id    VARCHAR(12)   NOT NULL REFERENCES invoices(invoice_id),
    claim_date    DATE,
    claim_amount  DECIMAL(12,2) CHECK (claim_amount > 0),
    claim_type    VARCHAR(30)   CHECK (claim_type IN ('Theft','Glass Damage','Fire','Accident','Natural Disaster')),
    status        VARCHAR(20)   CHECK (status IN ('Open','Approved','Under Review','Rejected')),
    fraud_label   SMALLINT      CHECK (fraud_label IN (0, 1)),
    description   TEXT
);

COMMENT ON TABLE  claims                IS 'Central fact table. One row per insurance claim.';
COMMENT ON COLUMN claims.claim_id      IS 'Primary key. Format: CLM followed by 5 digits.';
COMMENT ON COLUMN claims.fraud_label   IS
    '0 = Legitimate, 1 = Fraud. SYNTHETIC ground-truth label. Not real fraud evidence.';
COMMENT ON COLUMN claims.invoice_id    IS
    'References invoices.invoice_id. A single invoice may be referenced by '
    'multiple claims (source-data characteristic).';

-- ─────────────────────────────────────────────────────────────────────────────
-- LOCATIONS
-- Source: data/relational/locations.csv
-- Natural PK: location_id (LOC001 – LOC060)
-- NOTE: This table has NO FK from any other table. City string matching is
--       the only possible join. This is a source-data limitation.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE locations (
    location_id  VARCHAR(8)   NOT NULL PRIMARY KEY,
    city         VARCHAR(40),
    latitude     DECIMAL(9,6),
    longitude    DECIMAL(9,6)
);

COMMENT ON TABLE  locations               IS
    'Geographic coordinate reference. Orphaned: no FK references it. '
    'Join only via city string match. Source-data limitation.';
COMMENT ON COLUMN locations.location_id IS 'Primary key. Format: LOC followed by 3 digits.';
COMMENT ON COLUMN locations.latitude    IS 'Decimal degrees. India bounding box: lat 6–36, lon 68–98.';
