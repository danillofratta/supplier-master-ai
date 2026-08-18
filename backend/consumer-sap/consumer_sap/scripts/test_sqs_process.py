import asyncio
import os

from consumer_sap.infrastructure.integrations.sap.fake_sap_gateway import FakeSapGateway
from consumer_sap.infrastructure.messaging.sqs_consumer import SqsConsumer
from consumer_sap.infrastructure.messaging.sqs_message_mapper import SqsMessageMapper
from consumer_sap.features.sync_supplier.handler import SyncSupplierHandler
from consumer_sap.infrastructure.persistence.in_memory import InMemorySapIntegrationUnitOfWork

from dotenv import load_dotenv

load_dotenv()

async def main() -> None:
    print("Starting consumer test...")

    sqs_consumer = SqsConsumer(
        queue_url=os.environ["SQS_SAP_REQUEST_QUEUE_URL"],
        region_name=os.environ["AWS_REGION"],
    )
    
    unit_of_work = InMemorySapIntegrationUnitOfWork()
    sap_gateway = FakeSapGateway()

    handler = SyncSupplierHandler(unit_of_work=unit_of_work, sap_gateway=sap_gateway)

    print("Waiting for messages...")

    messages = await sqs_consumer.receive_messages()

    print(f"Messages received: {len(messages)}")

    for message in messages:
        command = SqsMessageMapper.to_sync_supplier_command(message)

        print(f"Processing message: {command.message_id}")

        result = await handler.handle(command)

        if result is None:
            print(f"Message {command.message_id} has already been processed.")
            continue

        print("SAP synchronization completed")
        print(
            "Business Partner:",
            result.business_partner_id,
        )
        print(
            "SAP Supplier:",
            result.sap_supplier_id,
        )

        print(
            "Inbox messages:",
            len(unit_of_work.inbox.items),
        )

        print(
            "SAP operations:",
            len(unit_of_work.operations.items),
        )

        print(
            "Outbox messages:",
            len(unit_of_work.outbox_messages.items),
        )

if __name__ == "__main__":
    asyncio.run(main())        