from dataclasses import dataclass

from src.entity.intermediate_store import IntermediateStore
from src.entity.sink import Sink
from src.entity.source import Source
from src.production.base.coordinates import Coordinates
from src.entity.machine.machine import Machine
from src.constant.constant import TransportRobotStatus

@dataclass
class TrWorkingStatus:
    status: TransportRobotStatus
    working_on_status: bool
    waiting_time_on_path: int

    driving_destination_coordinates: Coordinates | None
    driving_route: list[Coordinates] | None
    destination_location_entity: Machine | Source | Sink | IntermediateStore | None

    side_step_driving_route: list[Coordinates] | None

    waiting_error_time: int | None



