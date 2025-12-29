# app/ml/preprocess.py
import pickle
import pandas as pd
from app.ml.model import FEATURES

ENCODERS_PATH = "models/label_encoders.pkl"

# Загружаем label encoders
with open(ENCODERS_PATH, "rb") as f:
    LABEL_ENCODERS = pickle.load(f)


def preprocess_for_model(df: pd.DataFrame) -> pd.DataFrame:
    """
   Преобразование данных в формат, подходящий для модели:
    - label encoding категориальных признаков
    - удаление ненужных колонок
    - заполнение пропусков
    - приведение к нужному порядку колонок FEATURES
    """

    df = df.copy()

    # 1. Label encoding
    for col, encoder in LABEL_ENCODERS.items():
        if col in df.columns:
            df[col] = df[col].astype(str)
            df[col] = df[col].map(
                lambda v: v if v in encoder.classes_ else encoder.classes_[0]
            )
            df[col] = encoder.transform(df[col])

    # 2. Удаляем ненужные поля
    df = df.drop(
        columns=["user_email", "first_reg_date", "last_reg_date"], 
        errors="ignore"
    )

    # 3. Заполняем пропуски
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    # 4. Порядок признаков модели
    df = df.reindex(columns=FEATURES, fill_value=0)

    if list(df.columns) != FEATURES:
        raise ValueError("❌ Feature contract broken")

    return df
