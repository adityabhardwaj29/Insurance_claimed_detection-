export type UserRole = 'ADMIN' | 'CLAIMS_OFFICER' | 'INVESTIGATOR' | 'SUPERVISOR' | 'ANALYST';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  department?: string;
  badge_number?: string;
}

export interface Customer {
  id: string;
  customer_number: string;
  first_name: string;
  last_name: string;
  national_id?: string;
  phone?: string;
  email?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  risk_tier?: string;
  created_at: string;
}

export interface Policy {
  id: string;
  policy_number: string;
  claimant_id?: string;
  policy_type: string;
  status: string;
  start_date: string;
  end_date: string;
  deductible: number;
  coverage_limit: number;
  annual_premium?: number;
}

export interface Vehicle {
  id?: string;
  vin?: string;
  make: string;
  model: string;
  year: number;
  license_plate?: string;
}

export interface Claim {
  id: string;
  claim_number: string;
  policy_number?: string;
  policy_id?: string;
  claimant_id?: string;
  claimant_name?: string;
  incident_date: string;
  report_date: string;
  incident_type: string;
  collision_type?: string;
  incident_severity: string;
  incident_state?: string;
  incident_city?: string;
  incident_hour_of_the_day?: number;
  number_of_vehicles_involved?: number;
  bodily_injuries?: number;
  witnesses?: number;
  police_report_available?: string;
  total_claim_amount: number;
  injury_claim?: number;
  property_claim?: number;
  vehicle_claim?: number;
  vehicle_make?: string;
  vehicle_model?: string;
  auto_year?: number;
  auto_vin?: string;
  provider_id?: string;
  provider_name?: string;
  status: 'SUBMITTED' | 'UNDER_REVIEW' | 'ANALYZED' | 'ESCALATED_SIU' | 'APPROVED' | 'REJECTED' | 'CLOSED';
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_score?: number;
  created_at: string;
}

export interface RiskAnalysis {
  claim_id: string;
  claim_number: string;
  hybrid_risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  recommendation: 'AUTO_APPROVE' | 'FAST_TRACK' | 'MANUAL_INVESTIGATION' | 'SIU_ESCALATE';
  recommendation_reason: string;
  decision_status?: string;
  ml_score: number;
  anomaly_score: number;
  duplicate_score: number;
  graph_score: number;
  weights: {
    ml_weight: number;
    anomaly_weight: number;
    duplicate_weight: number;
    graph_weight: number;
  };
  top_risk_factors: Array<{
    feature: string;
    description: string;
    impact: number;
    contribution: string;
    value?: any;
  }>;
  duplicate_matches: Array<{
    matched_claim_id: string;
    matched_claim_number: string;
    similarity_score: number;
    match_reasons: string[];
    shared_attributes: Record<string, any>;
  }>;
  graph_syndicate: {
    suspicious_cluster_found: boolean;
    cluster_size: number;
    shared_entities: Array<{
      type: string;
      value: string;
      connected_claims: string[];
    }>;
    risk_indicators: string[];
  };
}

export interface InvestigationCase {
  id: string;
  case_number: string;
  claim_id: string;
  claim_number: string;
  claimant_name?: string;
  total_claim_amount: number;
  status: 'OPEN' | 'IN_PROGRESS' | 'EVIDENCE_COLLECTION' | 'PENDING_APPROVAL' | 'RESOLVED_FRAUD' | 'RESOLVED_LEGITIMATE' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  assigned_to?: string;
  investigator_name?: string;
  risk_score: number;
  created_at: string;
  updated_at: string;
  notes_count?: number;
  evidence_count?: number;
}

export interface CaseNote {
  id: string;
  case_id: string;
  author_name: string;
  author_role: string;
  content: string;
  created_at: string;
}

export interface CaseEvidence {
  id: string;
  case_id: string;
  title: string;
  document_type: string;
  file_url: string;
  uploaded_by: string;
  notes?: string;
  uploaded_at: string;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  user_email: string;
  user_role: string;
  action: string;
  entity_type: string;
  entity_id: string;
  details: string;
  ip_address?: string;
}

export interface DashboardKPIs {
  total_claims: number;
  total_claims_amount: number;
  active_investigations: number;
  fraud_detected_count: number;
  fraud_amount_prevented: number;
  avg_risk_score: number;
  high_risk_percentage: number;
  automation_rate: number;
}
