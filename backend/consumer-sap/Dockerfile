FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY consumer_sap ./consumer_sap
RUN pip install --no-cache-dir -e ".[observability]"
CMD ["python", "-m", "consumer_sap.main"]
