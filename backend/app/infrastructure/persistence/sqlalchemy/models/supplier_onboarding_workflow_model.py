from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.persistence.sqlalchemy.base import Base


class SupplierOnboardingWorkflowModel(Base):
    __tablename__ = "supplier_onboarding_workflow"

    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )
    supplier_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    service_now_ticket_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    sap_business_partner_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    rejection_reason: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    failure_reason: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
