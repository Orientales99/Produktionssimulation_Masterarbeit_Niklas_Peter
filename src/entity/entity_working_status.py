from dataclasses import dataclass

from src.production.base.coordinates import Coordinates
from src.entity.machine import Machine


@dataclass
class EntityWorkingStatus:
    driving_to_new_location: bool = False
    driving_destination: Coordinates | None = None
    driving_route: list[Coordinates] | None = None
    working_for_machine: Machine | None = None
    waiting_for_order: bool = True
    waiting_time_on_path: int = 5
