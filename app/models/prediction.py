# app/models/prediction.py
from datetime import datetime
from sqlmodel import SQLModel, Field

class Prediction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_email: str = Field(index=True)
    risk_score: float
    decision: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
