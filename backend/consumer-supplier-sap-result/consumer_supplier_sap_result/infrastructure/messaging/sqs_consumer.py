import asyncio

import boto3


class SqsConsumer:
    def __init__(
        self,
        *,
        queue_url: str,
        region_name: str,
    ) -> None:
        self._queue_url = queue_url
        self._client = boto3.client(
            "sqs",
            region_name=region_name,
        )

    async def receive_messages(
        self,
        *,
        max_messages: int = 10,
        wait_time_seconds: int = 20,
        visibility_timeout: int = 60,
    ) -> list[dict]:
        response = await asyncio.to_thread(
            self._client.receive_message,
            QueueUrl=self._queue_url,
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
            QueueUrl=self._queue_url,
            ReceiptHandle=receipt_handle,
        )
