from dataclasses import dataclass

from src.data.coordinates import Coordinates
from src.data.product import Product


@dataclass
class TransportRobot:
    identification_number: int
    product: Product | None
    robot_size: Coordinates
    driving_speed: int
    loaded_capacity: int
    max_loading_capacity: int
