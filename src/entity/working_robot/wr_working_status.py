from dataclasses import dataclass

from src.constant.constant import WorkingRobotStatus
from src.production.base.coordinates import Coordinates
from src.entity.machine.machine import Machine


@dataclass
class WrWorkingStatus:
    status: WorkingRobotStatus
    working_on_status: bool
    in_production: bool

    waiting_time_on_path: int

    working_for_machine: Machine | None
    driving_destination_coordinates: Coordinates | None
    driving_route: list[Coordinates] | None

    side_step_driving_route: list[Coordinates] | None

    last_placement_in_production: list | None


