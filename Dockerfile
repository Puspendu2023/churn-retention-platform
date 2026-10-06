FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MODEL_PATH=/app/models/churn_model.pkl
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir pandas numpy scikit-learn streamlit plotly openpyxl joblib matplotlib
COPY src/ src/
COPY models/churn_model.pkl models/churn_model.pkl
COPY data/processed/customer_data_clean.csv data/processed/customer_data_clean.csv
RUN useradd -m appuser && chown -R appuser /app
USER appuser
EXPOSE 8501
HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8501/_stcore/health')"
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
