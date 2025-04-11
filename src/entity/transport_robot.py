from dataclasses import dataclass, field
from simpy import Store
from src.entity.entity_working_status import EntityWorkingStatus
from src.entity.machine import Machine
from src.entity.transport_order import TransportOrder
from src.order_data.production_material import ProductionMaterial
from src.production.base.coordinates import Coordinates
from src.order_data.product import Product


@dataclass
class TransportRobot:
    identification_number: int
    size: Coordinates
    loading_speed: int
    driving_speed: int
    material_store: Store
    working_status: EntityWorkingStatus
    transport_order: TransportOrder = field(default=None)

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"TR: {self.identification_number}"
