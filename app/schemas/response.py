# app/api/schemas/response.py
from pydantic import BaseModel

class PredictResponse(BaseModel):
    user_email: str
    risk_score: float
    decision: str
