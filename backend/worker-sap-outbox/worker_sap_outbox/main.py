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


async def run() -> None:
    engine = create_async_engine(
        os.environ["SAP_INTEGRATION_DATABASE_URL"],
        pool_pre_ping=True,
    )
    factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    handler = PublishOutboxHandler(
        unit_of_work=SqlAlchemySapOutboxUnitOfWork(
            factory
        ),
        publisher=SqsMessagePublisher(
            queue_url=os.environ[
                "SQS_SAP_RESULT_QUEUE_URL"
            ],
            region_name=os.environ["AWS_REGION"],
        ),
    )

    interval = float(
        os.getenv(
            "OUTBOX_POLL_INTERVAL_SECONDS",
            "2",
        )
    )

    print("worker-sap-outbox started")

    try:
        while True:
            result = await handler.handle(
                PublishOutboxCommand(limit=50)
            )

            if result.published or result.failed:
                print(
                    f"Outbox published={result.published} "
                    f"failed={result.failed}"
                )

            await asyncio.sleep(interval)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
