from dataclasses import dataclass

from src.production.base.coordinates import Coordinates
from src.entity.machine.machine import Machine


@dataclass
class WrWorkingStatus:

    driving_to_new_location: bool = False
    waiting_for_order: bool = True
    waiting_time_on_path: int = 5

    driving_destination_work_on_machine: Coordinates | None = None
    driving_route_work_on_machine: list[Coordinates] | None = None
    working_for_machine: Machine | None = None
