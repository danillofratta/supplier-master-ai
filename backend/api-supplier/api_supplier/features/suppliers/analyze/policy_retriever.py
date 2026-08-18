from typing import Protocol

from api_supplier.features.suppliers.analyze.policy_context import PolicyContext


class PolicyRetriever(Protocol):
    async def retrieve(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> tuple[PolicyContext, ...]:
        ...
