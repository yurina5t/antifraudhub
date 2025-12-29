# app/ml/fe.py
import numpy as np
import pandas as pd

def apply_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    
    for col in ["first_reg_date", "last_reg_date"]:
        if col in df:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df["avg_sale_amount"] = df["avg_sale_amount"].fillna(0)
    df["avg_sale_amount_log"] = np.log1p(df["avg_sale_amount"])
    df["max_sale_amount_log"] = np.log1p(df["max_sale_amount"])
    df["min_sale_amount_log"] = np.log1p(df["min_sale_amount"])
    df["sales_freq"] = df["n_sales"] / (df["n_active_days"] + 1)
    df["declines_freq"] = df["n_declines"] / (df["n_active_days"] + 1)
    df["trial_ratio"] = df["n_trials"] / (df["n_sales"] + 1)
    df["pressure_score"] = df["n_declines"] - df["n_rebills"] + df["geo_mismatch_any"] * 2
    df["site_risk"] = (df["unique_sites"] >= 3).astype(int)
    df["affiliate_risk"] = (df["unique_affiliates"] >= 3).astype(int)
    df["cross_high"] = (df["cross_ratio"] > 0.5).astype(int)
    df["card_hopper_flag"] = (df["unique_card_brands"] > 1).astype(int)

    return df
