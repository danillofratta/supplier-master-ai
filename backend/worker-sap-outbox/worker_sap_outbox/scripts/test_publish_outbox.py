import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from worker_sap_outbox.features.publish_outbox.command import (
    PublishOutboxCommand,
)
from worker_sap_outbox.features.publish_outbox.handler import (
    PublishOutboxHandler,
)
from worker_sap_outbox.infrastructure.messaging.sqs_message_publisher import (
    SqsMessagePublisher,
)
from worker_sap_outbox.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemySapOutboxUnitOfWork,
)


load_dotenv()


async def main() -> None:
    print("Starting SAP outbox publisher...")

    engine = create_async_engine(
        os.environ[
            "SAP_INTEGRATION_DATABASE_URL"
        ]
    )

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    unit_of_work = (
        SqlAlchemySapOutboxUnitOfWork(
            session_factory
        )
    )

    publisher = SqsMessagePublisher(
        queue_url=os.environ[
            "SQS_SAP_RESULT_QUEUE_URL"
        ],
        region_name=os.environ["AWS_REGION"],
    )

    handler = PublishOutboxHandler(
        unit_of_work=unit_of_work,
        publisher=publisher,
    )

    result = await handler.handle(
        PublishOutboxCommand(
            limit=10
        )
    )

    print(
        f"Published: {result.published}"
    )
    print(
        f"Failed: {result.failed}"
    )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())