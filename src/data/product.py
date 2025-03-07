from dataclasses import dataclass

from src.data.coordinates import Coordinates

from src.data.constant import ItemType, ProductGroup


@dataclass
class Product:
    product_id: ProductGroup
    size: Coordinates               # Europalette = 100 units
    item_type: ItemType


