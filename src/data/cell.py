from src.data.machine import Machine
from src.data.sink import Sink
from src.data.source import Source
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


class Cell:
    # 400 mm x 400 mm ≙ 1 Cell
    x_coordinate: int
    y_coordinate: int
    placed_entity: Machine | TransportRobot | WorkingRobot | Source | Sink | None

    def __init__(self, x_coordinate, y_coordinate, placed_entity):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.placed_entity = placed_entity
