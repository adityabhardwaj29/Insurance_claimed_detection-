from pydantic import BaseModel
class ClaimRequest(BaseModel):
    claim_id: str
