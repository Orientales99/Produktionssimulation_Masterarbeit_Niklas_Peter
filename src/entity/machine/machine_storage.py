from dataclasses import dataclass

from simpy import Store
from src.order_data.product import Product
from src.order_data.production_material import ProductionMaterial


@dataclass
class MachineStorage:
    storage_before_process: Store
    storage_after_process: Store


