# AI-Powered Customer Intelligence and Retention Platform

**Project ID:** BCA-S6-MAJOR-AI-001 | UG BCA | Semester 6 | Major Project
**Anonymised client:** CustomerTech India
**Integrated subjects:** Business Analytics, Software Engineering, Machine Learning, Cloud-Native Development

## Problem statement
CustomerTech India has growing customer data but no integrated way to identify churn risk, explain customer behaviour, and turn insight into timely retention action. This project builds a working academic prototype that combines business analytics, a machine-learning churn model, disciplined software engineering, and a cloud-native deployment design.

Predictions produced by this prototype are **decision support, not guaranteed outcomes**.

## Tech stack
Python, pandas, scikit-learn, Streamlit, SQLite, Git, Docker.

## Repository layout
```
data/raw/            original dataset (customer_data.xlsx)
data/processed/      cleaned dataset (created in Phase 3/5)
notebooks/           01_eda.ipynb (Phase 4)
src/                 data_prep.py, train_model.py, evaluate_model.py, app.py
models/              churn_model.pkl (Phase 6)
tests/               test_cases.md (Phase 11)
docs/                requirements, data dictionary, model evaluation, architecture
```

## Setup
```bash
git clone <your-repo-url> churn-retention-platform
cd churn-retention-platform
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Verify the data loads:
```bash
python -c "import pandas as pd; print(pd.read_excel('data/raw/customer_data.xlsx').shape)"
```

## Build status
- [x] Phases 0-13 built: pipeline, EDA, model, evaluation, app, tests, Dockerfile, report
- [ ] Phase 14 - student review, signatures, screenshots, Docker build check

## Run
```bash
python -m src.data_prep && python -m src.train_model && python -m src.evaluate_model
pytest
streamlit run src/app.py
python report/build_report.py     # regenerates the PDF report
```
Docker (not yet built in the authoring environment): `docker build -t churn-platform . && docker run -p 8501:8501 churn-platform`
