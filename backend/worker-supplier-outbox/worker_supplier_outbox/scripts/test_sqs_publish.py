import asyncio
import os
from uuid import uuid4

from dotenv import load_dotenv

from worker_supplier_outbox.infrastructure.messaging.sqs_message_publisher import (
    SqsMessagePublisher,
)

load_dotenv()

async def main() -> None:
    queue_url = os.environ["SQS_SAP_REQUEST_QUEUE_URL"]
    region_name = os.environ["AWS_REGION"]

    publisher = SqsMessagePublisher(
        queue_url=queue_url,
        region_name=region_name,
    )

    await publisher.publish(
        event_type="supplier.sap-sync.requested.v1",
        message_id=str(uuid4()),
        payload = """
        {
            "message_id": "11111111-1111-1111-1111-111111111111",
            "workflow_id": "22222222-2222-2222-2222-222222222222",
            "supplier_id": "33333333-3333-3333-3333-333333333333",
            "name": "ACME Supplies",
            "email": "contact@acme.com",
            "phone": "11999999999",
            "tax_id": "12.345.678/0001-90",
            "address": {
                "street": "Main Street",
                "city": "Sao Paulo",
                "state": "SP",
                "zip_code": "01000-000",
                "country": "Brazil"
            }
        }
        """
    )

    print("Message successfully sent to SQS.")


if __name__ == "__main__":
    asyncio.run(main())