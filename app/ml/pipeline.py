# app/ml/pipeline.py
import pandas as pd

from app.ml.fetch import fetch_user_features
from app.ml.fe import apply_feature_engineering
from app.ml.preprocess import preprocess_for_model
from app.ml.model import predict
from app.core.decision import make_decision


# ---------------- BATCH ----------------

def run_batch_pipeline(client) -> pd.DataFrame:
    df_struct = fetch_user_features(client)
    df_struct = apply_feature_engineering(df_struct)

    df_preprocessed = preprocess_for_model(df_struct)

    results = []

    for idx, row in df_preprocessed.iterrows():
        user_email = df_struct.loc[idx, "user_email"]

        X = row.to_frame().T
        risk = predict(X)
        decision = make_decision(risk)

        results.append({
            "user_email": user_email,
            "risk_score": risk,
            "decision": decision.value
        })

    return pd.DataFrame(results)


# ---------------- SINGLE USER ----------------

def run_single_user_pipeline(client, user_email: str) -> dict| None:
    df_struct = fetch_user_features(client)
    print("REQUEST EMAIL:", repr(user_email))
    print(df_struct["user_email"].head(20).tolist())
    email = user_email.strip().lower()
    #df_user = df_struct[df_struct["user_email"] == user_email]
    df_struct["user_email_norm"] = (df_struct["user_email"].astype(str).str.strip().str.lower())

    df_user = df_struct[df_struct["user_email_norm"] == email]

    if df_user.empty:
        return None  

    df_user = apply_feature_engineering(df_user)
    X = preprocess_for_model(df_user).iloc[[0]]

    risk = predict(X)
    decision = make_decision(risk)

    return {
        "user_email": user_email,
        "risk_score": risk,
        "decision": decision.value
    }

