from uuid import UUID

from pydantic import BaseModel


class GetSupplierByIdResponse(BaseModel):
    supplier_id: UUID
    name: str
    email: str
    phone: str
    tax_id: str
    status: str
    street: str
    city: str
    state: str
    zip_code: str
    country: str
