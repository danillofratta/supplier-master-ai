from backend.app.features.suppliers.sync_to_sap.command import (
    SyncSupplierToSapCommand,
)
from backend.app.features.suppliers.sync_to_sap.exceptions import (
    SupplierNotFoundForSapSyncError,
)
from backend.app.features.suppliers.sync_to_sap.result import (
    SyncSupplierToSapResult,
)
from backend.app.features.suppliers.sync_to_sap.sap_supplier_gateway import (
    SapSupplierGateway,
)
from backend.app.shared.unit_of_work import SupplierUnitOfWork


class SyncSupplierToSapHandler:
    def __init__(
        self,
        unit_of_work: SupplierUnitOfWork,
        sap_gateway: SapSupplierGateway,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._sap_gateway = sap_gateway

    async def handle(
        self,
        command: SyncSupplierToSapCommand,
    ) -> SyncSupplierToSapResult:
        async with self._unit_of_work as uow:
            supplier = await uow.suppliers.get_by_id(
                command.supplier_id
            )

            if supplier is None:
                raise SupplierNotFoundForSapSyncError(
                    command.supplier_id
                )

            existing_reference = (
                await self._sap_gateway.find_by_tax_id(
                    supplier.tax_id
                )
            )

            if existing_reference is not None:
                return SyncSupplierToSapResult(
                    supplier_id=supplier.supplier_id,
                    business_partner_id=(
                        existing_reference.business_partner_id
                    ),
                    sap_supplier_id=(
                        existing_reference.supplier_id
                    ),
                    already_existed=True,
                )

            reference = await self._sap_gateway.create_supplier(
                supplier
            )

            return SyncSupplierToSapResult(
                supplier_id=supplier.supplier_id,
                business_partner_id=(
                    reference.business_partner_id
                ),
                sap_supplier_id=reference.supplier_id,
                already_existed=False,
            )
