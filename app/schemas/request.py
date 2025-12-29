# app/api/schemas/request.py
from pydantic import BaseModel

class PredictRequest(BaseModel):
    user_email: str
