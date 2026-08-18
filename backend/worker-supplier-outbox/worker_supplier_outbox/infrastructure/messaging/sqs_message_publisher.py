import asyncio
import json

import boto3


class SqsMessagePublisher:
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

    async def publish(
        self,
        *,
        event_type: str,
        payload: str,
        message_id: str,
    ) -> None:
        attributes = {
            "event_type": {
                "DataType": "String",
                "StringValue": event_type,
            },
            "message_id": {
                "DataType": "String",
                "StringValue": message_id,
            },
        }

        try:
            envelope = json.loads(payload)
            correlation_id = envelope.get(
                "correlation_id"
            )
            if correlation_id:
                attributes["correlation_id"] = {
                    "DataType": "String",
                    "StringValue": str(correlation_id),
                }
        except (TypeError, ValueError):
            pass

        await asyncio.to_thread(
            self._client.send_message,
            QueueUrl=self._queue_url,
            MessageBody=payload,
            MessageAttributes=attributes,
        )
