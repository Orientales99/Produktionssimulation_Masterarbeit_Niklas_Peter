from dataclasses import dataclass

from src.entity.sink import Sink
from src.entity.source import Source
from src.production.base.coordinates import Coordinates
from src.entity.machine import Machine


@dataclass
class EntityWorkingStatus:
    # Every Entity
    driving_to_new_location: bool = False
    waiting_for_order: bool = True
    waiting_time_on_path: int = 5

    # WorkingMachine
    driving_destination_work_on_machine: Coordinates | None = None
    driving_route_work_on_machine: list[Coordinates] | None = None
    working_for_machine: Machine | None = None

    # TransportMachine
    driving_destination_pick_up_material: Coordinates | None = None
    driving_route_pick_up_material: list[Coordinates] | None = None
    pick_up_location_entity: Machine | Source | None = None

    driving_destination_unload_material: Coordinates | None = None
    driving_route_unload_material: list[Coordinates] | None = None
    unload_location_entity: Machine | Source | Sink | None = None
