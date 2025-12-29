# app/ml/model.py
import pickle


MODEL_PATH = "models/fraud_model.pkl"

with open(MODEL_PATH, "rb") as f:
    payload = pickle.load(f)

automl = payload["automl"]        
FEATURES = payload["features"]
BEST_THRESHOLD = payload.get("best_threshold")
    
def predict(X) -> float:
    """
    X — уже полностью готовая матрица признаков
    """
    
    proba = float(automl.predict_proba(X)[0, 1])
    return  float(proba)
