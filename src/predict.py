"""Business-logic / model-serving layer: prediction, risk bands, recommended actions."""
import os
import joblib
import pandas as pd
from src.data_prep import FEATURES, CATEGORICAL, NUMERIC, ROOT

MODEL_PATH = os.environ.get("MODEL_PATH", str(ROOT / "models" / "churn_model.pkl"))
LOW_MAX, HIGH_MIN = 0.35, 0.55

ACTIONS = {
    "Low": "Maintain normal engagement: include in regular newsletters and loyalty communication.",
    "Medium": "Proactive check-in: send a personalised offer or app-engagement nudge and review recent support tickets.",
    "High": "Priority retention call: assign an account owner, resolve open support/payment issues and offer a tailored incentive.",
}
BOUNDS = {"Tenure_Months": (0, 120), "Monthly_Spend_INR": (0, 1_000_000), "Transactions_90D": (0, 1000),
          "Support_Tickets_90D": (0, 1000), "Avg_Response_Hours": (0, 1000), "Satisfaction_Score": (1, 5),
          "App_Logins_30D": (0, 1000), "Days_Since_Last_Purchase": (0, 10000),
          "Discount_Usage_Pct": (0, 100), "Payment_Failures_90D": (0, 1000)}

_model = None


def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def risk_band(p: float) -> str:
    return "High" if p >= HIGH_MIN else "Medium" if p >= LOW_MAX else "Low"


def validate_input(record: dict):
    missing = [f for f in FEATURES if f not in record or record[f] is None]
    if missing:
        raise ValueError(f"Missing fields: {missing}")
    for c, (lo, hi) in BOUNDS.items():
        if not lo <= record[c] <= hi:
            raise ValueError(f"{c}={record[c]} outside allowed range {lo}-{hi}")


def predict_one(record: dict) -> dict:
    validate_input(record)
    p = float(load_model().predict_proba(pd.DataFrame([record])[FEATURES])[:, 1][0])
    band = risk_band(p)
    return {"probability": p, "band": band, "action": ACTIONS[band]}


def top_drivers(record: dict, n=3):
    """Return the n features pushing this customer's score up the most (coef x standardised value)."""
    m = load_model(); prep, clf = m.named_steps["prep"], m.named_steps["clf"]
    x = prep.transform(pd.DataFrame([record])[FEATURES])
    x = x.toarray() if hasattr(x, "toarray") else x
    names = [s.split("__")[1] for s in prep.get_feature_names_out()]
    contrib = sorted(zip(names, (x[0] * clf.coef_[0])), key=lambda t: -t[1])
    return [(a, float(b)) for a, b in contrib[:n]]
