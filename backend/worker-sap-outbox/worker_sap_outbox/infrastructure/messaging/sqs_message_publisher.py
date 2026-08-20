import asyncio
import json

import boto3

from worker_sap_outbox.shared.observability import (
    inject_sqs_trace_attributes,
)



class SqsMessagePublisher:
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
                "SQS publisher requires queue_url or queue_name."
            )

    def _resolve_queue_url(self) -> str:
        if self._queue_url is not None:
            return self._queue_url

        response = self._client.get_queue_url(
            QueueName=self._queue_name,
        )
        self._queue_url = response["QueueUrl"]
        return self._queue_url

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

        attributes = (
            inject_sqs_trace_attributes(
                attributes
            )
        )

        await asyncio.to_thread(
            self._client.send_message,
            QueueUrl=self._resolve_queue_url(),
            MessageBody=payload,
            MessageAttributes=attributes,
        )
