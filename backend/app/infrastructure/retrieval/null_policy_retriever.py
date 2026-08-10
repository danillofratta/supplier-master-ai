from backend.app.features.suppliers.analyze.policy_context import PolicyContext


class NullPolicyRetriever:
    """Safe fallback until a real retrieval provider is configured."""

    async def retrieve(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> tuple[PolicyContext, ...]:
        return ()
