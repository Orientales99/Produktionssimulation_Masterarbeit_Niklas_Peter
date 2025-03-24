from dataclasses import dataclass

from simpy import Store
from src.gruppe_eins.product import Product


@dataclass
class MachineStorage:
    storage_before_process: Store
    product_before_process: Product | None
    storage_after_process: Store
    product_after_process: Product | None

