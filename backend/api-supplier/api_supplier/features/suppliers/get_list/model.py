from uuid import UUID

from pydantic import BaseModel


class SupplierListItemResponse(BaseModel):
    supplier_id: UUID
    name: str
    email: str
    tax_id: str
    status: str


class ListSuppliersResponse(BaseModel):
    items: list[SupplierListItemResponse]
