from dataclasses import dataclass

from src.data.coordinates import Coordinates


@dataclass
class WorkingRobot:
    identification_number: int
    robot_size: Coordinates
    driving_speed: int
    product_transfer_rate: int


