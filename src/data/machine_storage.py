from dataclasses import dataclass

from simpy import Store, Environment
from src.data.product import Product


@dataclass
class MachineStorage:
    storage_before_process: Store
    product_before_process: Product
    storage_after_process: Store
    product_after_process: Product

