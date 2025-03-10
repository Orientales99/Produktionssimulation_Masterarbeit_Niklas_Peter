from dataclasses import dataclass

from src.data.coordinates import Coordinates


@dataclass
class WorkingRobot:
    identification_number: int
    robot_size: Coordinates
    driving_speed: int
    product_transfer_rate: int

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"WR: {self.identification_number}"
