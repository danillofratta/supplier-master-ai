

import boto3
import asyncio

class SqsMessagePublisher:
    def __init__(
            self,
            *,
            queue_url: str,
            region_name: str,
    ) -> None:
        self.queue_url = queue_url
        self.region_name = region_name
        self._client = boto3.client("sqs", region_name=self.region_name)

    async def publish(
            self,
            *,
            event_type: str,
            payload: str,
            message_id: str,
    ) -> None:
        await asyncio.to_thread(
            self._client.send_message,
            QueueUrl=self.queue_url,
            MessageBody=payload,
            MessageAttributes={
                "event_type": {
                    "StringValue": event_type,
                    "DataType": "String"
                },
                "message_id": {
                    "StringValue": message_id,
                    "DataType": "String"
                }
            }
        )