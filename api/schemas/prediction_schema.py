from pydantic import BaseModel
class PredictionResponse(BaseModel):
    claim_id: str
    risk_score: float
    priority: str
