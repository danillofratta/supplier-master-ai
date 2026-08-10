from backend.app.domain.entities.address import Address
from backend.app.domain.entities.supplier import Supplier
from backend.app.domain.enums.supplier_status import SupplierStatus
from backend.app.infrastructure.persistence.sqlalchemy.models.supplier_model import (
    SupplierModel,
)


class SupplierMapper:
    @staticmethod
    def to_model(supplier: Supplier) -> SupplierModel:
        return SupplierModel(
            supplier_id=supplier.supplier_id,
            name=supplier.name,
            email=supplier.email,
            phone=supplier.phone,
            tax_id=supplier.tax_id,
            normalized_tax_id=SupplierMapper.normalize_tax_id(supplier.tax_id),
            status=supplier.status.value,
            street=supplier.address.street,
            city=supplier.address.city,
            state=supplier.address.state,
            zip_code=supplier.address.zip_code,
            country=supplier.address.country,
            created_at=supplier.created_at,
            updated_at=supplier.updated_at,
        )

    @staticmethod
    def to_domain(model: SupplierModel) -> Supplier:
        return Supplier(
            supplier_id=model.supplier_id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            tax_id=model.tax_id,
            status=SupplierStatus(model.status),
            address=Address(
                street=model.street,
                city=model.city,
                state=model.state,
                zip_code=model.zip_code,
                country=model.country,
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def normalize_tax_id(tax_id: str) -> str:
        return "".join(
            character.lower()
            for character in tax_id
            if character.isalnum()
        )
