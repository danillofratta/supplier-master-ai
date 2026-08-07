from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.app.domain.entities.address import Address
from backend.app.domain.enums.supplier_status import SupplierStatus
from backend.app.domain.exceptions import DomainError


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Supplier:
    supplier_id: UUID
    name: str
    email: str
    phone: str
    tax_id: str
    address: Address
    status: SupplierStatus = SupplierStatus.DRAFT
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    @classmethod
    def create(
        cls,
        name: str,
        email: str,
        phone: str,
        tax_id: str,
        address: Address,
    ) -> "Supplier":
        if not name.strip():
            raise DomainError("Supplier name cannot be empty.")
        if not tax_id.strip():
            raise DomainError("Supplier tax ID cannot be empty.")

        return cls(
            supplier_id=uuid4(),
            name=name,
            email=email,
            phone=phone,
            tax_id=tax_id,
            address=address,
        )

    def submit_for_review(self) -> None:
        if self.status != SupplierStatus.DRAFT:
            raise DomainError(
                "Only draft suppliers can be submitted for review."
            )
        if not self.name.strip():
            raise DomainError("Supplier name cannot be empty.")
        if not self.tax_id.strip():
            raise DomainError("Supplier tax ID cannot be empty.")

        self.status = SupplierStatus.UNDER_REVIEW
        self._touch()

    def can_be_approved(self) -> bool:
        return self.status == SupplierStatus.UNDER_REVIEW

    def approve(self) -> None:
        if not self.can_be_approved():
            raise DomainError(
                "Supplier must be under review to be approved."
            )
        self.status = SupplierStatus.APPROVED
        self._touch()

    def reject(self) -> None:
        if self.status != SupplierStatus.UNDER_REVIEW:
            raise DomainError(
                "Supplier must be under review to be rejected."
            )
        self.status = SupplierStatus.REJECTED
        self._touch()

    def _touch(self) -> None:
        self.updated_at = utc_now()
