from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str
