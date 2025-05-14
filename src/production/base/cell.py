from dataclasses import dataclass

from src.entity.intermediate_store import IntermediateStore
from src.production.base.coordinates import Coordinates
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot


@dataclass
class Cell:
    # 400 mm x 400 mm ≙ 1 Cell
    cell_coordinates: Coordinates
    placed_entity: Machine | TransportRobot | WorkingRobot | Source | Sink | IntermediateStore | None
    neighbors_list = []

    @property  # only if cell_id is used; one time calculation -> is cached
    def cell_id(self) -> str:
        return f"{self.cell_coordinates.x}:{self.cell_coordinates.y}"
