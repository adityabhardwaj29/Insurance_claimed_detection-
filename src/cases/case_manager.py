class CaseManager:
    def create_case(self, claim_id, risk_score):
        return {"claim_id":claim_id,"risk_score":risk_score,"status":"OPEN"}
