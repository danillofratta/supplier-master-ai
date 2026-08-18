from consumer_supplier_sap_result.features.complete_sap_sync.handler import (
    CompleteSapSyncHandler,
)
from consumer_supplier_sap_result.features.fail_sap_sync.handler import (
    FailSapSyncHandler,
)
from consumer_supplier_sap_result.infrastructure.messaging.sqs_message_mapper import (
    SAP_SYNC_COMPLETED_V1,
    SAP_SYNC_FAILED_V1,
    SqsMessageMapper,
)


class SapResultMessageProcessor:
    def __init__(
        self,
        complete_handler: CompleteSapSyncHandler,
        fail_handler: FailSapSyncHandler,
    ) -> None:
        self._complete_handler = complete_handler
        self._fail_handler = fail_handler

    async def process(
        self,
        message: dict,
    ) -> None:
        event_type = SqsMessageMapper.get_event_type(
            message
        )

        if event_type == SAP_SYNC_COMPLETED_V1:
            command = SqsMessageMapper.to_complete_command(
                message
            )
            await self._complete_handler.handle(command)
            return

        if event_type == SAP_SYNC_FAILED_V1:
            command = SqsMessageMapper.to_fail_command(
                message
            )
            await self._fail_handler.handle(command)
            return

        raise ValueError(
            f"Unsupported SAP result event '{event_type}'."
        )
