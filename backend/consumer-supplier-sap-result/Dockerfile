FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY consumer_supplier_sap_result ./consumer_supplier_sap_result
RUN pip install --no-cache-dir -e ".[observability]"
CMD ["python", "-m", "consumer_supplier_sap_result.main"]
