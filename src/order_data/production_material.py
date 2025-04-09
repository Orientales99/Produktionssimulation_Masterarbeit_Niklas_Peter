from dataclasses import dataclass

from src.production.base.coordinates import Coordinates

from src.constant.constant import ItemType, ProductGroup


@dataclass
class ProductionMaterial:
    identification_str: str                 # Example: ProductGroup.SEVEN.0
    production_material_id: ProductGroup
    size: Coordinates
    item_type: ItemType

