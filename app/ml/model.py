# app/ml/model.py
import pickle
import numpy as np
import pandas as pd

MODEL_PATH = "models/fraud_model.pkl"

with open(MODEL_PATH, "rb") as f:
    payload = pickle.load(f)

model = payload["automl"]        
FEATURES = payload["features"]
BEST_THRESHOLD = payload.get("best_threshold")
    
def predict(X: pd.DataFrame) -> np.ndarray:
    """
     X : pd.DataFrame
        shape (n_samples, n_features)
        Полностью подготовленные model-ready признаки.
    """
    
    return model.predict_proba(X)[:, 1]