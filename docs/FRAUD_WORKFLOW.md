# End-to-End Operational Claims & SIU Investigation Workflow

## 1. Operational Journey Map

```
  +-------------------------------------------------------------------------+
  |  STEP 1: CUSTOMER INTAKE & VERIFICATION                                 |
  |  Claims Officer identifies claimant via National ID / Driver License    |
  +-------------------------------------------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |  STEP 2: AUTOMATED POLICY VERIFICATION                                  |
  |  System verifies active coverage dates, deductible, and coverage limits  |
  +-------------------------------------------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |  STEP 3: MULTI-STEP CLAIM INTAKE                                        |
  |  - Collision circumstances, loss hour, severity, city, and state         |
  |  - Financial breakdown: Bodily injury, property, and vehicle damage     |
  |  - Supporting evidence: Police report, repair estimate, scene photos    |
  +-------------------------------------------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |  STEP 4: AUTOMATED MULTI-SIGNAL FRAUD PIPELINE                          |
  |  1. 38 feature vectors engineered and scaled                             |
  |  2. Supervised XGBoost inference (ML score)                             |
  |  3. Isolation Forest outlier calculation (Anomaly score)                |
  |  4. Duplicate claim hash lookup across historical VINs (Duplicate score)|
  |  5. Bipartite graph collusion scan (Graph score)                        |
  |  6. Blended Hybrid Risk Score computed (0.0 to 1.0)                     |
  |  7. SHAP feature attribution waterfall generated                        |
  +-------------------------------------------------------------------------+
                                       |
            +--------------------------+--------------------------+
            |                                                     |
  [Risk Score >= 0.50]                                   [Risk Score < 0.25]
            |                                                     |
            v                                                     v
  +-----------------------------------------+   +---------------------------+
  |  STEP 5A: SIU ESCALATION & CASE CREATION|   |  STEP 5B: STRAIGHT-THRU   |
  |  - Investigation docket auto-created    |   |  - Automated approval     |
  |  - Priority flagged (HIGH or CRITICAL)  |   |  - Payment disbursement   |
  |  - Assigned to SIU Investigator         |   |  - Claim closed           |
  +-----------------------------------------+   +---------------------------+
            |
            v
  +-------------------------------------------------------------------------+
  |  STEP 6: FORENSIC INVESTIGATION & EVIDENCE REVIEW                       |
  |  - Investigator reviews 360° Claim Dossier                              |
  |  - Reviews duplicate matches and interactive syndicate network graph    |
  |  - Adds forensic notes and interviews claimant                          |
  +-------------------------------------------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |  STEP 7: HUMAN DISPOSITION DECISION                                     |
  |  Supervisor or Investigator records official determination:              |
  |  - APPROVE: Claim legitimate, cleared for settlement                    |
  |  - REJECT: Formal denial issued with corroborated fraud evidence        |
  |  - ESCALATE_LEGAL: Forwarded to law enforcement / legal prosecution     |
  +-------------------------------------------------------------------------+
                                       |
                                       v
  +-------------------------------------------------------------------------+
  |  STEP 8: IMMUTABLE AUDIT LOGGING                                        |
  |  Event cryptographically recorded with operator ID, role, and timestamp |
  +-------------------------------------------------------------------------+
```

---

## 2. Investigator Action Checklist

When reviewing an escalated high-risk claim in the 360° Dossier:
1. **Inspect Composite Score:** Note the primary signal driving the score (ML probability, anomaly outlier, duplicate match, or graph collusion).
2. **Review SHAP Waterfall:** Identify the exact features that elevated risk above the 0.50 threshold.
3. **Verify Duplicate Matches:** If duplicate matches exist, inspect the matched claim number and check for identical VINs or recycled estimates.
4. **Explore Syndicate Graph:** Determine if the repair shop, medical clinic, or attorney is linked to other suspicious claims.
5. **Record Decision & Notes:** Enter factual notes detailing findings, attach any newly obtained evidence, and record the final disposition.
