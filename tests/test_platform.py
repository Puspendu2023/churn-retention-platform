import pandas as pd, pytest, joblib
from src import data_prep as dp
from src.predict import predict_one, risk_band, validate_input
from src.train_model import MODEL_PATH, make_pipeline

BASE = {"Age_Group": "25-34", "Region": "East", "Customer_Segment": "Value", "Tenure_Months": 24,
        "Monthly_Spend_INR": 4800, "Transactions_90D": 9, "Support_Tickets_90D": 3, "Avg_Response_Hours": 15.0,
        "Satisfaction_Score": 3, "App_Logins_30D": 17, "Days_Since_Last_Purchase": 60,
        "Discount_Usage_Pct": 40, "Payment_Failures_90D": 2}

def test_tc01_data_loads():
    df = dp.load_raw(); assert df.shape == (2200, 15) and list(df.columns[:1]) == ["Customer_ID"]

def test_tc02_missing_values_handled():
    df = dp.load_raw(); df.loc[0, "Monthly_Spend_INR"] = None
    out = dp.clean(df); assert out["Monthly_Spend_INR"].isna().sum() == 0

def test_tc03_encoding_excludes_id_and_shape():
    df = dp.clean(dp.load_raw()); pre = dp.build_preprocessor().fit(df[dp.FEATURES])
    names = pre.get_feature_names_out()
    assert not any("Customer_ID" in n for n in names) and len(names) == 5 + 5 + 3 + 10

def test_tc04_stratified_split():
    df = dp.clean(dp.load_raw()); _, _, ytr, yte = dp.get_split(df)
    assert abs(ytr.mean() - yte.mean()) < 0.01 and len(yte) == 440

def test_tc05_training_runs():
    df = dp.clean(dp.load_raw()); Xtr, _, ytr, _ = dp.get_split(df)
    m = make_pipeline("Logistic Regression").fit(Xtr, ytr); assert hasattr(m, "predict_proba")

def test_tc06_prediction_valid_probability():
    out = predict_one(BASE); assert 0 <= out["probability"] <= 1 and out["band"] in {"Low", "Medium", "High"}

def test_tc07_risk_bands_and_actions():
    assert (risk_band(0.1), risk_band(0.4), risk_band(0.9)) == ("Low", "Medium", "High")
    assert predict_one(BASE)["action"]

def test_tc08_dashboard_filter_logic():
    df = dp.clean(dp.load_raw()); f = df[(df.Customer_Segment == "Premium") & (df.Region == "West")]
    assert 0 < len(f) < len(df) and set(f.Customer_Segment) == {"Premium"}

def test_tc09_edge_zero_tenure():
    r = dict(BASE, Tenure_Months=0); assert 0 <= predict_one(r)["probability"] <= 1

def test_tc10_invalid_input_rejected():
    with pytest.raises(ValueError): validate_input(dict(BASE, Satisfaction_Score=9))
    with pytest.raises(ValueError): validate_input({k: v for k, v in BASE.items() if k != "Region"})

def test_tc11_no_pii_in_model_inputs():
    assert "Customer_ID" not in dp.FEATURES

def test_tc12_data_quality_clean():
    v = dp.validate(dp.load_raw()); assert v["missing_values"] == 0 and v["duplicate_ids"] == 0 and v["discount_out_of_bounds"] == 0
