from dataclasses import dataclass

from src.production.base.coordinates import Coordinates

from src.constant.constant import ItemType, ProductGroup


@dataclass
class ProductionMaterial:
    identification_str: str
    production_material_id: ProductGroup
    size: Coordinates  # Europalette = 100 units
    item_type: ItemType

