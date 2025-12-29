import pandas as pd
from app.ml.preprocess import preprocess_for_model
from app.ml.model import FEATURES

def test_preprocess_contract():
    raw_df = pd.DataFrame([{
        "user_email": "test@example.com"
    }])

    X = preprocess_for_model(raw_df)

    assert list(X.columns) == FEATURES
    assert X.shape[1] == len(FEATURES)
