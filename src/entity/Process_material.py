from dataclasses import dataclass

from src.order_data.production_material import ProductionMaterial


@dataclass
class ProcessMaterial:
    required_material: ProductionMaterial
    quantity_required: int
    produceing_material: ProductionMaterial
    quantity_producing: int