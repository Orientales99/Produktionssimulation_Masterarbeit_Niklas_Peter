from dataclasses import dataclass

from src.order_data.production_material import ProductionMaterial


@dataclass
class GoodReceipt:
    production_material: ProductionMaterial
    quantity: int
    time: int