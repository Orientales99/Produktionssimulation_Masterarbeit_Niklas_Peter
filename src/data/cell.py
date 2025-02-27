from src.data.coordinates import Coordinates
from src.data.machine import Machine
from src.data.sink import Sink
from src.data.source import Source
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


class Cell:
    # 400 mm x 400 mm ≙ 1 Cell
    cell_coordinates: Coordinates
    placed_entity: Machine | TransportRobot | WorkingRobot | Source | Sink | None

    def __init__(self, cell_coordinates, placed_entity):
        self.cell_coordinates = cell_coordinates
        self.placed_entity = placed_entity
