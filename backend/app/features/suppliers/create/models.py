from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain.entities.supplier import Supplier
from backend.app.domain.enums.supplier_status import SupplierStatus


class AddressRequest(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(str_strip_whitespace=True)

    street: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=50)
    state: str = Field(min_length=1, max_length=50)
    zip_code: str = Field(min_length=1, max_length=20)
    country: str = Field(min_length=1, max_length=50)


class CreateSupplierRequest(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=100)
    phone: str = Field(min_length=1, max_length=20)
    tax_id: str = Field(min_length=5, max_length=30)
    address: AddressRequest


class CreateSupplierResponse(BaseModel):
    supplier_id: UUID
    name: str
    email: str
    phone: str
    tax_id: str
    status: SupplierStatus
    address: AddressRequest

    @classmethod
    def from_domain(cls, supplier: Supplier) -> "CreateSupplierResponse":
        return cls(
            supplier_id=supplier.supplier_id,
            name=supplier.name,
            email=supplier.email,
            phone=supplier.phone,
            tax_id=supplier.tax_id,
            status=supplier.status,
            address=AddressRequest(
                street=supplier.address.street,
                city=supplier.address.city,
                state=supplier.address.state,
                zip_code=supplier.address.zip_code,
                country=supplier.address.country,
            ),
        )


@dataclass(frozen=True, slots=True)
class CreateSupplierAddressCommand:
    street: str
    city: str
    state: str
    zip_code: str
    country: str


@dataclass(frozen=True, slots=True)
class CreateSupplierCommand:
    name: str
    email: str
    phone: str
    tax_id: str
    address: CreateSupplierAddressCommand
