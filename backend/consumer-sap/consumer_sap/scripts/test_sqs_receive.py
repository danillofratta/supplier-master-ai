import asyncio
import os
from consumer_sap.infrastructure.messaging.sqs_consumer import SqsConsumer
from consumer_sap.infrastructure.messaging.sqs_message_mapper import (
    SqsMessageMapper,
)

from dotenv import load_dotenv


load_dotenv()


async def main() -> None:
    consumer = SqsConsumer(
        queue_url=os.environ["SQS_SAP_REQUEST_QUEUE_URL"],
        region_name=os.environ["AWS_REGION"],
    )

    print("AWS_REGION:", os.environ["AWS_REGION"])
    print("QUEUE_URL:", os.environ["SQS_SAP_REQUEST_QUEUE_URL"])

    print("Waiting for messages...")

    messages = await consumer.receive_messages()

    print(f"Messages received: {len(messages)}")

    for message in messages:
        command = (
            SqsMessageMapper.to_sync_supplier_command(message)
        )

        print()
        print("Message ID:", command.message_id)
        print("Workflow ID:", command.workflow_id)
        print("Supplier ID:", command.supplier_id)
        print("Supplier:", command.name)
        print("Tax ID:", command.tax_id)
        print("City:", command.address.city)


if __name__ == "__main__":
    asyncio.run(main())