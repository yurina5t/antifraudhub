# app/ml/pipeline.py
import pandas as pd

from app.ml.fetch import fetch_user_features_batch, fetch_user_features_user
from app.ml.fe import apply_feature_engineering
from app.ml.preprocess import preprocess_for_model
from app.ml.model import predict
from app.core.decision import make_decision


# ---------------- BATCH ----------------

def run_batch_pipeline(client, active_days=7, feature_days=365) -> pd.DataFrame:
    """
    Batch-пайплайн:
    ClickHouse → features → model → decision
    """
    df_struct = fetch_user_features_batch(client, active_days=active_days, feature_days=feature_days)

    if df_struct.empty:
        return df_struct

    df_fe = apply_feature_engineering(df_struct)
    X = preprocess_for_model(df_fe)

    risks = predict(X)
    df_struct["risk_score"] = risks
    df_struct["decision"] = df_struct["risk_score"].apply(
        lambda r: make_decision(r).value
    )

    return df_struct[["user_email", "risk_score", "decision"]]

# ---------------- SINGLE USER ----------------

def run_single_user_pipeline(client, user_email: str, feature_days: int = 365)-> dict | None:
    """
    Realtime-пайплайн для одного пользователя
    """
    df_struct = fetch_user_features_user(client, user_email=user_email, feature_days=feature_days)
    if df_struct.empty:
        return None  

    df_fe = apply_feature_engineering(df_struct)
    X = preprocess_for_model(df_fe)

    risk = float(predict(X)[0])
    decision = make_decision(risk).value

    return {
        "user_email": user_email,
        "risk_score": risk,
        "decision": decision,
    }
