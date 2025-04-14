from dataclasses import dataclass, field
from simpy import Store
from src.entity.transport_robot.tr_working_status import TrWorkingStatus
from src.entity.transport_robot.transport_order import TransportOrder
from src.production.base.coordinates import Coordinates


@dataclass
class TransportRobot:
    identification_number: int
    size: Coordinates
    loading_speed: int
    driving_speed: int
    material_store: Store
    working_status: TrWorkingStatus
    transport_order: TransportOrder = field(default=None)

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"TR: {self.identification_number}"

