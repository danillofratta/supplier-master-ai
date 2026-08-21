from api_supplier.features.suppliers.request_review.command import (
    RequestSupplierReviewCommand,
)
from api_supplier.features.suppliers.request_review.exceptions import (
    SupplierNotFoundForReviewError,
)
from api_supplier.features.suppliers.request_review.models import (
    SupplierReviewRequestDto,
)
from api_supplier.features.suppliers.request_review.result import (
    RequestSupplierReviewResult,
)
from api_supplier.features.suppliers.request_review.servicenow_gateway import (
    ServiceNowGateway,
)
from api_supplier.shared.unit_of_work import (
    SupplierUnitOfWork,
)


class RequestSupplierReviewHandler:
    def __init__(
        self,
        unit_of_work: SupplierUnitOfWork,
        servicenow_gateway: ServiceNowGateway,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._servicenow_gateway = (
            servicenow_gateway
        )

    async def handle(
        self,
        command: RequestSupplierReviewCommand,
    ) -> RequestSupplierReviewResult:
        # Load local state first and release the DB session before the
        # external ServiceNow call. The network operation does not need to
        # hold an open PostgreSQL unit of work.
        async with self._unit_of_work as uow:
            supplier = await uow.suppliers.get_by_id(
                command.supplier_id
            )

        if supplier is None:
            raise SupplierNotFoundForReviewError(
                command.supplier_id
            )

        review_request = SupplierReviewRequestDto(
            supplier_id=supplier.supplier_id,
            supplier_name=supplier.name,
            tax_id=supplier.tax_id,
            risk_level=command.risk_level,
            reason=command.reason,
            policy_ids=command.policy_ids,
        )

        ticket = (
            await self._servicenow_gateway
            .create_review_ticket(
                review_request
            )
        )

        return RequestSupplierReviewResult(
            supplier_id=supplier.supplier_id,
            ticket_id=ticket.ticket_id,
            ticket_number=ticket.ticket_number,
            status=ticket.status,
        )
