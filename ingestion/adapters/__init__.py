from dataclasses import dataclass, field

@dataclass(frozen=True)
class BankAdapter:
    name: str
    column_map: dict[str, str] # maps bank header to canonical name
    date_format: str
    amount_columns: tuple[str, ...] = field(default_factory=tuple)

from adapters.chase import CHASE
from adapters.boa import BOA

REGISTRY: dict[str, BankAdapter] = {
    CHASE.name: CHASE,
    BOA.name: BOA,
}

def get_adapter(bank_id: str) -> BankAdapter | None:
    return REGISTRY.get(bank_id)