from src.data.coordinates import Coordinates
from src.data.product import Product


class TransportRobot:
    identification_number: int
    driving_speed: int
    robot_size: Coordinates
    loaded_capacity: int
    max_loading_capacity: int
    product: Product | None

    def __init__(self, identification_number, product, robot_size, driving_speed, loaded_capacity,
                 max_loading_capacity):
        self.identification_number = identification_number
        self.product = product
        self.robot_size = robot_size
        self.driving_speed = driving_speed
        self.loaded_capacity = loaded_capacity
        self.max_loading_capacity = max_loading_capacity
