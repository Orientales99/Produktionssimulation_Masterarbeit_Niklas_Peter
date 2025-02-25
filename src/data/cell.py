from src.data.machine import Machine
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


class Cell:
    # 400 mm x 400 mm ≙ 1 Cell
    x_coordinate: int
    y_coordinate: int
    machine: Machine | None
    transport_robot: TransportRobot | None
    working_robot: WorkingRobot | None
    source: bool
    sink: bool

    def __init__(self, x_coordinate, y_coordinate, machine, transport_robot, working_robot, source, sink):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.machine = machine
        self.transport_robot = transport_robot
        self.working_robot = working_robot
        self.source = source
        self.sink = sink
