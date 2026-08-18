from api_supplier.features.suppliers.create.models import (
    CreateSupplierAddressCommand,
    CreateSupplierCommand,
    CreateSupplierRequest,
)


def map_request_to_command(
    request: CreateSupplierRequest,
) -> CreateSupplierCommand:
    """Map the HTTP request model to the application command."""
    return CreateSupplierCommand(
        name=request.name,
        email=request.email,
        phone=request.phone,
        tax_id=request.tax_id,
        address=CreateSupplierAddressCommand(
            street=request.address.street,
            city=request.address.city,
            state=request.address.state,
            zip_code=request.address.zip_code,
            country=request.address.country,
        ),
    )
