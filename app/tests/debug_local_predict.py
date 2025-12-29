# debug_pipeline_contract.py
import pandas as pd

from app.ml.model import predict, FEATURES
from app.ml.preprocess import preprocess_for_model

print("=== PIPELINE CONTRACT TEST ===")

# -------------------------------------------------
# 1. ФЕЙКОВЫЕ СЫРЫЕ ДАННЫЕ (как из ClickHouse)
# -------------------------------------------------

raw_df = pd.DataFrame([{
    "user_email": "test@example.com",
    # всё остальное допустимо пустым
}])

# -------------------------------------------------
# 2. PREPROCESS (ЕДИНАЯ ТОЧКА)
# -------------------------------------------------

df_full = preprocess_for_model(raw_df)

print("\nAfter preprocess:")
print(df_full.head())
print("Shape:", df_full.shape)

# -------------------------------------------------
# 3. ЖЁСТКИЙ FEATURE CONTRACT
# -------------------------------------------------

print("\n--- CONTRACT CHECK ---")
print("FEATURES len:", len(FEATURES))
print("X columns len:", df_full.shape[1])

extra = set(df_full.columns) - set(FEATURES)
missing = set(FEATURES) - set(df_full.columns)

assert not extra, f"❌ Extra columns: {extra}"
assert not missing, f"❌ Missing columns: {missing}"
assert list(df_full.columns) == FEATURES, "❌ Wrong feature order"

print("✅ Feature contract OK")

# -------------------------------------------------
# 4. PREDICT (через публичный API)
# -------------------------------------------------

try:
    proba = predict(df_full)
    print("\n✅ Prediction OK")
    print("Risk score:", proba)
except Exception as e:
    print("\n❌ Predict failed")
    raise
