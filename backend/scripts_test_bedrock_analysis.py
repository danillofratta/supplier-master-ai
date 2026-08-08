"""Manual Bedrock smoke test.

Run from the repository root after configuring AWS credentials and .env:
    python -m backend.scripts_test_bedrock_analysis

This script is intentionally excluded from the automated unit-test suite.
"""

import asyncio

from backend.app.domain.entities.address import Address
from backend.app.domain.entities.supplier import Supplier
from backend.app.infrastructure.ai.bedrock_supplier_analyzer import (
    BedrockSupplierAnalyzer,
)
from backend.app.bootstrap.settings import get_settings


async def main() -> None:
    settings = get_settings()
    if not settings.bedrock_model_id:
        raise RuntimeError("BEDROCK_MODEL_ID must be configured before running this script.")

    analyzer = BedrockSupplierAnalyzer(
        region_name=settings.aws_region,
        model_id=settings.bedrock_model_id,
        temperature=settings.bedrock_temperature,
        max_tokens=settings.bedrock_max_tokens,
    )
    supplier = Supplier.create(
        name="ACME Supplies",
        email="contact@acme.com",
        phone="+55 11 99999-9999",
        tax_id="12.345.678/0001-90",
        address=Address(
            street="Main Street",
            city="Sao Paulo",
            state="SP",
            zip_code="01000-000",
            country="Brazil",
        ),
    )

    result = await analyzer.analyze(supplier)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
