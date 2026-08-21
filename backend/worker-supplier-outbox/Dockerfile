FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY worker_supplier_outbox ./worker_supplier_outbox
RUN pip install --no-cache-dir -e ".[observability]"
CMD ["python", "-m", "worker_supplier_outbox.main"]
