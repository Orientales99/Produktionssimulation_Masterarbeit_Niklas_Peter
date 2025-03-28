from dataclasses import dataclass

from src.order_data.production_material import ProductionMaterial


@dataclass
class RequiredMaterial:
    required_material: ProductionMaterial
    quantity: int