from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from consumer_supplier_sap_result.infrastructure.persistence.sqlalchemy.base import (
    Base,
)


class WorkflowModel(Base):
    __tablename__ = "supplier_onboarding_workflow"

    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )
    correlation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    supplier_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    sap_business_partner_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    failure_reason: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )


class InboxMessageModel(Base):
    __tablename__ = "inbox_messages"

    message_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
