import asyncio

import boto3


class SqsConsumer:
    def __init__(
        self,
        *,
        queue_url: str | None,
        queue_name: str | None = None,
        region_name: str,
    ) -> None:
        self._queue_url = queue_url or None
        self._queue_name = queue_name or None
        self._client = boto3.client(
            "sqs",
            region_name=region_name,
        )

        if self._queue_url is None and self._queue_name is None:
            raise ValueError(
                "SQS consumer requires queue_url or queue_name."
            )

    def _resolve_queue_url(self) -> str:
        if self._queue_url is not None:
            return self._queue_url

        response = self._client.get_queue_url(
            QueueName=self._queue_name,
        )
        self._queue_url = response["QueueUrl"]
        return self._queue_url

    async def receive_messages(
        self,
        *,
        max_messages: int = 10,
        wait_time_seconds: int = 20,
        visibility_timeout: int = 60,
    ) -> list[dict]:
        response = await asyncio.to_thread(
            self._client.receive_message,
            QueueUrl=self._resolve_queue_url(),
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time_seconds,
            VisibilityTimeout=visibility_timeout,
            MessageAttributeNames=["All"],
            MessageSystemAttributeNames=[
                "ApproximateReceiveCount",
            ],
        )
        return response.get("Messages", [])

    async def delete_message(
        self,
        receipt_handle: str,
    ) -> None:
        await asyncio.to_thread(
            self._client.delete_message,
            QueueUrl=self._resolve_queue_url(),
            ReceiptHandle=receipt_handle,
        )
