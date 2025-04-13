from dataclasses import dataclass

from src.order_data.production_material import ProductionMaterial


@dataclass
class ProcessMaterial:
    required_material: ProductionMaterial
    quantity_required: int
    producing_material: ProductionMaterial
    quantity_producing: int
    required_material_on_tr_for_delivery: int = 0
