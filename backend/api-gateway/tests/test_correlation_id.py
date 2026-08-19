from uuid import UUID

from api_gateway.middleware.correlation_id import (
    resolve_correlation_id,
)


def test_preserves_valid_correlation_id() -> None:
    value = "11111111-1111-1111-1111-111111111111"

    assert resolve_correlation_id(value) == value


def test_replaces_invalid_correlation_id() -> None:
    generated = resolve_correlation_id(
        "not-a-uuid"
    )

    UUID(generated)
