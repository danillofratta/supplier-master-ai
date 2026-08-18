from typing import Protocol, Self
from consumer_supplier_sap_result.domain.repositories.workflow_repository import WorkflowRepository
from consumer_supplier_sap_result.domain.repositories.inbox_repository import InboxRepository

class SupplierResultUnitOfWork(Protocol):
    workflows: WorkflowRepository
    inbox: InboxRepository
    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...
    async def commit(self) -> None: ...
