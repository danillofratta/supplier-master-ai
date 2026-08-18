from typing import Protocol

from api_supplier.features.suppliers.request_review.models import (
    ServiceNowTicketDto,
    SupplierReviewRequestDto,
)


class ServiceNowGateway(Protocol):
    async def create_review_ticket(
        self,
        request: SupplierReviewRequestDto,
    ) -> ServiceNowTicketDto:
        ...

    async def get_review_ticket(
        self,
        ticket_id: str,
    ) -> ServiceNowTicketDto | None:
        ...
