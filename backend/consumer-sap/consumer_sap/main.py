import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from consumer_sap.features.sync_supplier.handler import (
    SyncSupplierHandler,
)
from consumer_sap.infrastructure.integrations.sap.fake_sap_gateway import (
    FakeSapGateway,
)
from consumer_sap.infrastructure.messaging.sqs_consumer import (
    SqsConsumer,
)
from consumer_sap.infrastructure.messaging.sqs_message_mapper import (
    SqsMessageMapper,
)
from consumer_sap.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemySapIntegrationUnitOfWork,
)


load_dotenv()


async def run() -> None:
    engine = create_async_engine(
        os.environ["SAP_INTEGRATION_DATABASE_URL"],
        pool_pre_ping=True,
    )
    factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    uow = SqlAlchemySapIntegrationUnitOfWork(factory)

    # This project intentionally uses a fake SAP adapter until a real
    # SAP/OData environment is available. The handler depends only on
    # the SapGateway protocol, so the adapter can be replaced later.
    handler = SyncSupplierHandler(
        unit_of_work=uow,
        sap_gateway=FakeSapGateway(),
    )

    consumer = SqsConsumer(
        queue_url=os.environ[
            "SQS_SAP_REQUEST_QUEUE_URL"
        ],
        region_name=os.environ["AWS_REGION"],
    )

    print("consumer-sap started (SAP adapter: fake)")

    try:
        while True:
            messages = await consumer.receive_messages()

            for message in messages:
                try:
                    command = (
                        SqsMessageMapper
                        .to_sync_supplier_command(message)
                    )

                    result = await handler.handle(command)

                    # ACK only after the local DB transaction commits.
                    # Duplicate deliveries are safe because of Inbox.
                    await consumer.delete_message(
                        message["ReceiptHandle"]
                    )

                    if result is None:
                        print(
                            "Duplicate SAP request ignored:",
                            command.message_id,
                        )
                    else:
                        print(
                            "SAP request completed:",
                            command.message_id,
                            result.business_partner_id,
                        )
                except Exception as exc:
                    # Do not delete. SQS visibility timeout and DLQ policy
                    # will cause a retry / eventual dead-lettering.
                    print(
                        "SAP request processing failed:",
                        message.get("MessageId"),
                        str(exc),
                    )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
