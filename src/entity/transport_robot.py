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
    loaded_material: list[ProductionMaterial] | None
    size: Coordinates
    driving_speed: int
    loaded_capacity: int
    max_loading_capacity: Store
    working_status: EntityWorkingStatus
    transport_order: list[TransportOrder] = field(
        default_factory=list)  # default: empty | list (destination Machine, transport Material, quantity)

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"TR: {self.identification_number}"
