from pydantic import BaseModel
class CaseResponse(BaseModel):
    claim_id: str
    status: str
