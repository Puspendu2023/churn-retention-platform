"""Data preparation: loading, cleaning, validation and feature pipeline.
This module never imports app.py (module boundary: data layer -> no UI dependency)."""
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "customer_data.xlsx"
CLEAN_PATH = ROOT / "data" / "processed" / "customer_data_clean.csv"

ID_COL = "Customer_ID"
TARGET = "Churned"
CATEGORICAL = ["Age_Group", "Region", "Customer_Segment"]
NUMERIC = ["Tenure_Months", "Monthly_Spend_INR", "Transactions_90D", "Support_Tickets_90D",
           "Avg_Response_Hours", "Satisfaction_Score", "App_Logins_30D",
           "Days_Since_Last_Purchase", "Discount_Usage_Pct", "Payment_Failures_90D"]
FEATURES = CATEGORICAL + NUMERIC
RANDOM_STATE = 42


def load_raw(path=RAW_PATH) -> pd.DataFrame:
    return pd.read_excel(path)


def validate(df: pd.DataFrame) -> dict:
    """Return a dict of data-quality findings (used by tests and docs)."""
    return {
        "rows": len(df),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_ids": int(df[ID_COL].duplicated().sum()),
        "discount_out_of_bounds": int(((df["Discount_Usage_Pct"] < 0) | (df["Discount_Usage_Pct"] > 100)).sum()),
        "satisfaction_out_of_bounds": int(((df["Satisfaction_Score"] < 1) | (df["Satisfaction_Score"] > 5)).sum()),
        "negative_numeric": int((df[NUMERIC] < 0).sum().sum()),
        "invalid_target": int((~df[TARGET].isin(["Yes", "No"])).sum()),
    }


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Light cleaning: strip text, drop duplicates, impute numeric gaps with median
    (none are expected in the supplied data, but the step keeps the pipeline robust)."""
    df = df.copy()
    for c in CATEGORICAL + [ID_COL, TARGET]:
        df[c] = df[c].astype(str).str.strip()
    df = df.drop_duplicates(subset=ID_COL)
    for c in NUMERIC:
        if df[c].isna().any():
            df[c] = df[c].fillna(df[c].median())
    return df.reset_index(drop=True)


def encode_target(series: pd.Series) -> pd.Series:
    return (series == "Yes").astype(int)


def build_preprocessor() -> ColumnTransformer:
    """One-hot encode nominal categories (no natural order in Region/Segment; age bands are
    handled the same way for simplicity) and standardise numeric fields (needed for Logistic
    Regression; harmless for tree models). Customer_ID is excluded by construction."""
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ("num", StandardScaler(), NUMERIC),
    ])


def get_split(df: pd.DataFrame, test_size=0.2):
    """Stratified split so train and test keep the same churn proportion."""
    X, y = df[FEATURES], encode_target(df[TARGET])
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=RANDOM_STATE)


def main():
    df = clean(load_raw())
    print("Validation:", validate(df))
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Saved {CLEAN_PATH} ({len(df)} rows)")


if __name__ == "__main__":
    main()
