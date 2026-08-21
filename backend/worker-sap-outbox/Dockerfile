FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY worker_sap_outbox ./worker_sap_outbox
RUN pip install --no-cache-dir -e ".[observability]"
CMD ["python", "-m", "worker_sap_outbox.main"]
