# app/core/decision.py
from enum import Enum
from app.core.config import get_settings

class Decision(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


def make_decision(risk_score: float) -> Decision:
    """
    3-zone antifraud decision logic
    """
    settings = get_settings()

    if risk_score >= settings.FRAUD_BLOCK_THRESHOLD:
        return Decision.BLOCK

    if risk_score >= settings.FRAUD_REVIEW_THRESHOLD:
        return Decision.REVIEW

    return Decision.ALLOW