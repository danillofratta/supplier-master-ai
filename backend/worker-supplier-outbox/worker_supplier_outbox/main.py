import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from worker_supplier_outbox.features.publish_outbox.command import (
    PublishOutboxCommand,
)
from worker_supplier_outbox.features.publish_outbox.handler import (
    PublishOutboxHandler,
)
from worker_supplier_outbox.infrastructure.messaging.sqs_message_publisher import (
    SqsMessagePublisher,
)
from worker_supplier_outbox.infrastructure.persistence.unit_of_work import (
    SqlAlchemyOutboxUnitOfWork,
)
from worker_supplier_outbox.shared.logging import (
    configure_logging,
)
from worker_supplier_outbox.shared.observability import (
    configure_tracing,
)


load_dotenv()
logger = configure_logging("worker-supplier-outbox")
tracer = configure_tracing("worker-supplier-outbox")


async def run() -> None:
    engine = create_async_engine(
        os.environ["SUPPLIER_DATABASE_URL"],
        pool_pre_ping=True,
    )
    factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    handler = PublishOutboxHandler(
        unit_of_work=SqlAlchemyOutboxUnitOfWork(
            factory
        ),
        publisher=SqsMessagePublisher(
            queue_url=os.environ[
                "SQS_SAP_REQUEST_QUEUE_URL"
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

    logger.info("worker started")

    try:
        while True:
            result = await handler.handle(
                PublishOutboxCommand(limit=50)
            )

            if result.published or result.failed:
                logger.info(
                    "outbox batch processed",
                    extra={
                        "published": result.published,
                        "failed": result.failed,
                    },
                )

            await asyncio.sleep(interval)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
