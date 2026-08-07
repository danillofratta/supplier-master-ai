from typing import Annotated

from fastapi import Depends

from backend.app.domain.repositories.supplier_repository import SupplierRepository
from backend.app.features.suppliers.create.handler import CreateSupplierHandler
from backend.app.infrastructure.supplier_repository import (
    InMemorySupplierRepository,
)

_repository_instance = InMemorySupplierRepository()


def get_supplier_repository() -> SupplierRepository:
    return _repository_instance


SupplierRepositoryDependency = Annotated[
    SupplierRepository,
    Depends(get_supplier_repository),
]


def get_create_supplier_handler(
    repository: SupplierRepositoryDependency,
) -> CreateSupplierHandler:
    return CreateSupplierHandler(repository)
