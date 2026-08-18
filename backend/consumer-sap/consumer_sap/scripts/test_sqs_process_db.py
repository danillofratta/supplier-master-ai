import asyncio
import os

from consumer_sap.infrastructure.integrations.sap.fake_sap_gateway import FakeSapGateway
from consumer_sap.infrastructure.messaging.sqs_consumer import SqsConsumer
from consumer_sap.infrastructure.messaging.sqs_message_mapper import SqsMessageMapper
from consumer_sap.features.sync_supplier.handler import SyncSupplierHandler
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from consumer_sap.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemySapIntegrationUnitOfWork,
)

from dotenv import load_dotenv

load_dotenv()

async def main() -> None:
    print("Starting consumer test...")

    sqs_consumer = SqsConsumer(
        queue_url=os.environ["SQS_SAP_REQUEST_QUEUE_URL"],
        region_name=os.environ["AWS_REGION"],
    )
    
    database_url = os.environ[
        "SAP_INTEGRATION_DATABASE_URL"
    ]

    engine = create_async_engine(
        database_url,
        echo=False,
    )

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    unit_of_work = SqlAlchemySapIntegrationUnitOfWork(
        session_factory
    )
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

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())        