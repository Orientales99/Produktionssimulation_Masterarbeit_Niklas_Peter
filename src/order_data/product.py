from dataclasses import dataclass

from src.production.base.coordinates import Coordinates

from src.constant.constant import ItemType, ProductGroup
from src.order_data.production_material import ProductionMaterial


@dataclass
class Product:
    product_id: ProductGroup
    size: Coordinates  # Europalette = 100 units
    item_type: ItemType

    required_product_type_step_1: ProductionMaterial | None
    processing_step_1: int | None
    processing_time_step_1: float | None

    required_product_type_step_2: ProductionMaterial | None
    processing_step_2: int | None
    processing_time_step_2: float | None

    required_product_type_step_3: ProductionMaterial | None
    processing_step_3: int | None
    processing_time_step_3: float | None

    required_product_type_step_4: ProductionMaterial | None
    processing_step_4: int | None
    processing_time_step_4: float | None

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"product {self.product_id}"
