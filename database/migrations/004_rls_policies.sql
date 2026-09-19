-- =============================================================================
-- database/migrations/004_rls_policies.sql
-- Production Supabase Row Level Security (RLS) Policies
-- =============================================================================

-- Enable Row Level Security on core application tables
ALTER TABLE claimants ENABLE ROW LEVEL SECURITY;
ALTER TABLE policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_scores ENABLE ROW LEVEL SECURITY;

-- ─────────────────────────────────────────────────────────────────────────────
-- Helper Function: Get current authenticated user role from JWT claims
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION current_user_role() RETURNS text AS $$
    SELECT coalesce(
        current_setting('request.jwt.claims', true)::jsonb ->> 'user_role',
        current_setting('request.jwt.claims', true)::jsonb -> 'app_metadata' ->> 'role',
        'CLAIMS_OFFICER'
    );
$$ LANGUAGE sql STABLE;

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS POLICIES FOR CLAIMS
-- ─────────────────────────────────────────────────────────────────────────────
-- Allow authenticated staff to view all claims
CREATE POLICY "Staff can view all claims" ON claims
    FOR SELECT TO authenticated
    USING (TRUE);

-- Claims officers and Admins can insert claims
CREATE POLICY "Claims officers can create claims" ON claims
    FOR INSERT TO authenticated
    WITH CHECK (
        current_user_role() IN ('CLAIMS_OFFICER', 'ADMIN', 'SUPERVISOR')
    );

-- Supervisors, Investigators, and Admins can update claim status
CREATE POLICY "Investigators and supervisors can update claims" ON claims
    FOR UPDATE TO authenticated
    USING (
        current_user_role() IN ('INVESTIGATOR', 'SUPERVISOR', 'ADMIN')
    );

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS POLICIES FOR INVESTIGATION CASES
-- ─────────────────────────────────────────────────────────────────────────────
-- All authenticated staff can view case queue
CREATE POLICY "Staff can view cases" ON investigation_cases
    FOR SELECT TO authenticated
    USING (TRUE);

-- Investigators and Supervisors can update cases
CREATE POLICY "Investigators can update cases" ON investigation_cases
    FOR UPDATE TO authenticated
    USING (
        current_user_role() IN ('INVESTIGATOR', 'SUPERVISOR', 'ADMIN')
    );

-- System and Claims Officers can create investigation cases
CREATE POLICY "Authorized staff can create cases" ON investigation_cases
    FOR INSERT TO authenticated
    WITH CHECK (
        current_user_role() IN ('CLAIMS_OFFICER', 'INVESTIGATOR', 'SUPERVISOR', 'ADMIN')
    );

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS POLICIES FOR CASE NOTES & EVIDENCE
-- ─────────────────────────────────────────────────────────────────────────────
CREATE POLICY "Staff can view notes" ON case_notes
    FOR SELECT TO authenticated USING (TRUE);

CREATE POLICY "Investigators can insert notes" ON case_notes
    FOR INSERT TO authenticated
    WITH CHECK (current_user_role() IN ('INVESTIGATOR', 'SUPERVISOR', 'ADMIN'));

CREATE POLICY "Staff can view evidence" ON case_evidence
    FOR SELECT TO authenticated USING (TRUE);

CREATE POLICY "Investigators can add evidence" ON case_evidence
    FOR INSERT TO authenticated
    WITH CHECK (current_user_role() IN ('INVESTIGATOR', 'SUPERVISOR', 'ADMIN'));

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS POLICIES FOR DOCUMENTS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE POLICY "Staff can view documents" ON documents
    FOR SELECT TO authenticated USING (TRUE);

CREATE POLICY "Staff can upload documents" ON documents
    FOR INSERT TO authenticated WITH CHECK (TRUE);

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS POLICIES FOR AUDIT LOGS (Append-only)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE POLICY "Admins and Supervisors can view audit logs" ON audit_logs
    FOR SELECT TO authenticated
    USING (current_user_role() IN ('ADMIN', 'SUPERVISOR', 'ANALYST'));

CREATE POLICY "System can append audit logs" ON audit_logs
    FOR INSERT TO authenticated WITH CHECK (TRUE);

-- ─────────────────────────────────────────────────────────────────────────────
-- SERVICE ROLE BYPASS
-- ─────────────────────────────────────────────────────────────────────────────
-- Backend services using the Supabase Service Role key bypass RLS automatically.
