# app/routes/fraud.py
import pandas as pd
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database.database import get_session
from app.services.clickhouse_client import get_clickhouse_client

from app.ml.pipeline import run_batch_pipeline, run_single_user_pipeline
from app.ml.model import predict, FEATURES
from app.models.prediction import Prediction
from app.schemas.response import PredictResponse
from app.core.runtime import get_worker_mode
from app.core.decision import Decision

fraud_route = APIRouter()

WORKER_MODE = get_worker_mode()

def store_prediction(db: Session, user_email: str, risk: float, decision: str):
    """
    Сохраняет предсказание в Postgres.
    """
    record = Prediction(
        user_email=user_email,
        risk_score=float(risk),
        decision=decision,
    )
    db.add(record)

@fraud_route.get("/health", summary="ML model healthcheck")
def fraud_healthcheck():
    """
    Проверяет:
    - что модель загружается
    - что preprocess + predict работают
    """
    try:
        # минимальный валидный input
        dummy = pd.DataFrame([{c: 0 for c in FEATURES}])
        _ = predict(dummy)

        return {
            "status": "ok",
            "worker_mode": WORKER_MODE,
            "features": len(FEATURES),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@fraud_route.post("/predict/batch")
def fraud_predict_batch(
    decision: Optional[List[Decision]] = None,
    ch_client=Depends(get_clickhouse_client),
    db: Session = Depends(get_session),
):
    """
    Batch-прогон всех пользователей:
    ClickHouse → pipeline → Postgres
    Можно фильтровать вывод:
    ?decision=REVIEW&decision=BLOCK
    """
    if WORKER_MODE != "batch":
        raise HTTPException(
            status_code=403,
            detail="Batch scoring is disabled on realtime workers"
        )
    
    df = run_batch_pipeline(ch_client)
    if decision:
        df = df[df["decision"].isin([d.value for d in decision])]

    for _, row in df.iterrows():
        store_prediction(
            db,
            row["user_email"],
            row["risk_score"],
            row["decision"],
        )

    db.commit()
    return df.to_dict(orient="records")


@fraud_route.get("/predict/user/{user_email}", response_model=PredictResponse)
def fraud_predict_user(
    user_email: str,
    ch_client=Depends(get_clickhouse_client),
    db: Session = Depends(get_session),
):
    """
    Прогноз фрода для одного пользователя.
    """
    if WORKER_MODE != "realtime":
        raise HTTPException(
            status_code=403,
            detail="Realtime scoring is disabled on batch workers"
        )

    result = run_single_user_pipeline(ch_client, user_email)

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    store_prediction(
        db,
        result["user_email"],
        result["risk_score"],
        result["decision"],
    )
    db.commit()

    return PredictResponse(**result)
