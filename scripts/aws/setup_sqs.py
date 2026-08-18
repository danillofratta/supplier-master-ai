import json
import os

import boto3


REGION = os.getenv("AWS_REGION", "us-east-2")
MAX_RECEIVE_COUNT = os.getenv(
    "SQS_MAX_RECEIVE_COUNT",
    "5",
)
PURGE_EXISTING = os.getenv(
    "SQS_PURGE_EXISTING",
    "false",
).lower() == "true"

REQUEST_QUEUE = os.getenv(
    "SQS_SAP_REQUEST_QUEUE_NAME",
    "supplier-sap-sync-requests",
)
REQUEST_DLQ = os.getenv(
    "SQS_SAP_REQUEST_DLQ_NAME",
    "supplier-sap-sync-requests-dlq",
)
RESULT_QUEUE = os.getenv(
    "SQS_SAP_RESULT_QUEUE_NAME",
    "supplier-sap-sync-results",
)
RESULT_DLQ = os.getenv(
    "SQS_SAP_RESULT_DLQ_NAME",
    "supplier-sap-sync-results-dlq",
)


def ensure_queue(
    sqs,
    name: str,
) -> str:
    response = sqs.create_queue(
        QueueName=name,
        Attributes={
            "ReceiveMessageWaitTimeSeconds": "20",
            "VisibilityTimeout": "60",
            "MessageRetentionPeriod": "345600",
        },
    )
    return response["QueueUrl"]


def queue_arn(
    sqs,
    queue_url: str,
) -> str:
    response = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=["QueueArn"],
    )
    return response["Attributes"]["QueueArn"]


def attach_dlq(
    sqs,
    queue_url: str,
    dlq_arn: str,
) -> None:
    redrive = {
        "deadLetterTargetArn": dlq_arn,
        "maxReceiveCount": MAX_RECEIVE_COUNT,
    }
    sqs.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={
            "RedrivePolicy": json.dumps(
                redrive,
                separators=(",", ":"),
            )
        },
    )


def main() -> None:
    sqs = boto3.client(
        "sqs",
        region_name=REGION,
    )

    request_dlq_url = ensure_queue(
        sqs,
        REQUEST_DLQ,
    )
    result_dlq_url = ensure_queue(
        sqs,
        RESULT_DLQ,
    )
    request_url = ensure_queue(
        sqs,
        REQUEST_QUEUE,
    )
    result_url = ensure_queue(
        sqs,
        RESULT_QUEUE,
    )

    attach_dlq(
        sqs,
        request_url,
        queue_arn(sqs, request_dlq_url),
    )
    attach_dlq(
        sqs,
        result_url,
        queue_arn(sqs, result_dlq_url),
    )

    if PURGE_EXISTING:
        for queue_url in (
            request_url,
            request_dlq_url,
            result_url,
            result_dlq_url,
        ):
            sqs.purge_queue(QueueUrl=queue_url)
        print("Existing SQS messages purged")

    print("SQS topology ready")
    print(
        "SQS_SAP_REQUEST_QUEUE_URL="
        + request_url
    )
    print(
        "SQS_SAP_RESULT_QUEUE_URL="
        + result_url
    )


if __name__ == "__main__":
    main()
