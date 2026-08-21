FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY api_supplier ./api_supplier
RUN pip install --no-cache-dir -e ".[runtime]"
CMD ["python", "-m", "uvicorn", "api_supplier.main:app", "--host", "0.0.0.0", "--port", "8001"]
