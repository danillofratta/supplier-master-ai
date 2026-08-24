FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY supplier_mcp ./supplier_mcp

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[observability]"

EXPOSE 8010

CMD ["python", "-m", "supplier_mcp.main"]
