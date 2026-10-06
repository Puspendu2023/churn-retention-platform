"""Streamlit UI layer. Run: streamlit run src/app.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import streamlit as st
import plotly.express as px
from src.data_prep import CLEAN_PATH, load_raw, clean, CATEGORICAL
from src.predict import predict_one, top_drivers

st.set_page_config(page_title="Customer Retention Platform", layout="wide")
st.title("AI-Powered Customer Intelligence and Retention Platform")
st.caption("Academic prototype - CustomerTech India (anonymised). Predictions are decision support, not guaranteed outcomes.")


@st.cache_data
def get_data():
    df = pd.read_csv(CLEAN_PATH) if Path(CLEAN_PATH).exists() else clean(load_raw())
    df["Churn_Flag"] = (df["Churned"] == "Yes").astype(int)
    return df


df = get_data()
tab1, tab2 = st.tabs(["KPI Dashboard", "Churn Risk Prediction"])

with tab1:  # FR-01, FR-04
    st.sidebar.header("Dashboard filters")
    seg = st.sidebar.multiselect("Segment", sorted(df.Customer_Segment.unique()), default=sorted(df.Customer_Segment.unique()))
    reg = st.sidebar.multiselect("Region", sorted(df.Region.unique()), default=sorted(df.Region.unique()))
    f = df[df.Customer_Segment.isin(seg) & df.Region.isin(reg)]
    if f.empty:
        st.warning("No customers match the selected filters.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Customers", f"{len(f):,}")
        c2.metric("Churn rate", f"{f.Churn_Flag.mean()*100:.1f}%")
        c3.metric("Avg satisfaction (churned)", f"{f[f.Churn_Flag==1].Satisfaction_Score.mean():.2f}" if (f.Churn_Flag==1).any() else "n/a")
        c4.metric("Avg monthly spend (INR)", f"{f.Monthly_Spend_INR.mean():,.0f}")
        a, b = st.columns(2)
        for col, container in [("Customer_Segment", a), ("Region", b)]:
            g = f.groupby(col).Churn_Flag.mean().mul(100).reset_index()
            container.plotly_chart(px.bar(g, x=col, y="Churn_Flag", labels={"Churn_Flag": "Churn rate (%)"},
                                          title=f"Churn rate by {col}"), width="stretch")
        g = f.groupby("Payment_Failures_90D").Churn_Flag.mean().mul(100).reset_index()
        st.plotly_chart(px.bar(g, x="Payment_Failures_90D", y="Churn_Flag", labels={"Churn_Flag": "Churn rate (%)"},
                               title="Churn rate by payment failures (90 days)"), width="stretch")

with tab2:  # FR-02, FR-03, FR-05, FR-06
    st.subheader("Enter customer attributes (no personal identifiers are collected)")
    with st.form("customer"):
        c1, c2, c3 = st.columns(3)
        age = c1.selectbox("Age group", ["18-24", "25-34", "35-44", "45-54", "55+"])
        region = c2.selectbox("Region", ["East", "West", "North", "Central", "South"])
        segment = c3.selectbox("Segment", ["Value", "Growth", "Premium"])
        tenure = c1.number_input("Tenure (months)", 0, 120, 24)
        spend = c2.number_input("Monthly spend (INR)", 0, 1_000_000, 4800)
        txn = c3.number_input("Transactions (90d)", 0, 1000, 9)
        tickets = c1.number_input("Support tickets (90d)", 0, 1000, 3)
        resp = c2.number_input("Avg response hours", 0.0, 1000.0, 15.0)
        sat = c3.slider("Satisfaction score", 1, 5, 3)
        logins = c1.number_input("App logins (30d)", 0, 1000, 17)
        recency = c2.number_input("Days since last purchase", 0, 10000, 60)
        disc = c3.number_input("Discount usage (%)", 0, 100, 40)
        fails = c1.number_input("Payment failures (90d)", 0, 1000, 2)
        go = st.form_submit_button("Predict churn risk")
    if go:
        rec = {"Age_Group": age, "Region": region, "Customer_Segment": segment, "Tenure_Months": tenure,
               "Monthly_Spend_INR": spend, "Transactions_90D": txn, "Support_Tickets_90D": tickets,
               "Avg_Response_Hours": resp, "Satisfaction_Score": sat, "App_Logins_30D": logins,
               "Days_Since_Last_Purchase": recency, "Discount_Usage_Pct": disc, "Payment_Failures_90D": fails}
        try:
            out = predict_one(rec)
            st.metric("Churn probability", f"{out['probability']*100:.1f}%")
            {"Low": st.success, "Medium": st.warning, "High": st.error}[out["band"]](f"Risk band: {out['band']}")
            st.info("Recommended action: " + out["action"])
            st.write("Top factors raising this customer's score:",
                     ", ".join(f"{n} ({v:+.2f})" for n, v in top_drivers(rec)))
            st.caption("Model is a weak-to-moderate signal (see report); use alongside human judgement.")
        except ValueError as e:
            st.error(str(e))
