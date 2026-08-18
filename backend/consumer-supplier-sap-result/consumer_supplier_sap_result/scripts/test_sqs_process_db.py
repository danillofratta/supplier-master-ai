import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from consumer_supplier_sap_result.features.complete_sap_sync.handler import (
    CompleteSapSyncHandler,
)
from consumer_supplier_sap_result.features.fail_sap_sync.handler import (
    FailSapSyncHandler,
)
from consumer_supplier_sap_result.features.process_sap_result.processor import (
    SapResultMessageProcessor,
)
from consumer_supplier_sap_result.infrastructure.messaging.sqs_consumer import (
    SqsConsumer,
)
from consumer_supplier_sap_result.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemySupplierResultUnitOfWork,
)


load_dotenv()


async def main() -> None:
    engine = create_async_engine(
        os.environ["SUPPLIER_DATABASE_URL"],
        pool_pre_ping=True,
    )
    factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    uow = SqlAlchemySupplierResultUnitOfWork(factory)

    processor = SapResultMessageProcessor(
        CompleteSapSyncHandler(uow),
        FailSapSyncHandler(uow),
    )

    consumer = SqsConsumer(
        queue_url=os.environ[
            "SQS_SAP_RESULT_QUEUE_URL"
        ],
        region_name=os.environ["AWS_REGION"],
    )

    messages = await consumer.receive_messages()

    print(f"Messages received: {len(messages)}")

    for message in messages:
        await processor.process(message)
        await consumer.delete_message(
            message["ReceiptHandle"]
        )
        print(
            "Processed and deleted:",
            message["MessageId"],
        )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
