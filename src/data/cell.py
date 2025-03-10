from dataclasses import dataclass

from src.data.coordinates import Coordinates
from src.data.machine import Machine
from src.data.sink import Sink
from src.data.source import Source
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


@dataclass
class Cell:
    # 400 mm x 400 mm ≙ 1 Cell
    cell_id = ""
    cell_coordinates: Coordinates
    placed_entity: Machine | TransportRobot | WorkingRobot | Source | Sink | None
    neighbors_list = []


    def __post_init__(self):
        self.cell_id = self.get_cell_id()

    def get_cell_id(self) -> str:
        return f"{self.cell_coordinates.x}:{self.cell_coordinates.y}"