import asyncio

import boto3


class SqsConsumer:
    def __init__(
            self,
            *,
            queue_url: str,
            region_name: str,
    ) -> None:
        self.queue_url = queue_url
        self.region_name = region_name
        self._client = boto3.client("sqs", region_name=self.region_name)

    async def receive_messages(
            self
    ) -> list[dict]:
        response = await asyncio.to_thread(
            self._client.receive_message,
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,
            VisibilityTimeout=30,
            MessageAttributeNames=["All"]
        )
        return response.get("Messages", [])

    async def delete(
            self,
            receipt_handle: str
    ) -> None:
        await asyncio.to_thread(
            self._client.delete_message,
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )