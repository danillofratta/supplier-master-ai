from api_supplier.features.suppliers.request_review.models import (
    ServiceNowTicketDto,
    SupplierReviewRequestDto,
)


class FakeServiceNowGateway:
    def __init__(self) -> None:
        self.tickets: dict[str, ServiceNowTicketDto] = {}
        self.created_requests: list[SupplierReviewRequestDto] = []

    async def create_review_ticket(
        self,
        request: SupplierReviewRequestDto,
    ) -> ServiceNowTicketDto:
        ticket = ServiceNowTicketDto(
            ticket_id="sys-001",
            ticket_number="RITM0001001",
            status="OPEN",
        )

        self.created_requests.append(request)
        self.tickets[ticket.ticket_id] = ticket
        return ticket

    async def get_review_ticket(
        self,
        ticket_id: str,
    ) -> ServiceNowTicketDto | None:
        return self.tickets.get(ticket_id)
