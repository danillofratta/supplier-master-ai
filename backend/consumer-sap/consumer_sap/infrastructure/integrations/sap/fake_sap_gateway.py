from consumer_sap.features.sync_supplier.sap_gateway import SapSupplierDto
class FakeSapGateway:
    def __init__(self): self.items={}; self.create_calls=0
    async def find_by_tax_id(self, tax_id): return self.items.get(self._n(tax_id))
    async def create_supplier(self, supplier):
        self.create_calls += 1
        dto=SapSupplierDto("100000001","200000001")
        self.items[self._n(supplier.tax_id)] = dto
        return dto
    def seed(self, tax_id, dto): self.items[self._n(tax_id)] = dto
    @staticmethod
    def _n(v): return "".join(c.lower() for c in v if c.isalnum())
