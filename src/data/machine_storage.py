from dataclasses import dataclass

from simpy import Container, Environment
from src.data.product import Product


@dataclass
class MachineStorage:
    storage_before_process: Container
    product_before_process: Product
    storage_after_process: Container
    product_after_process: Product

