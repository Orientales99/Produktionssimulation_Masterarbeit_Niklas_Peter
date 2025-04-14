from dataclasses import dataclass

from src.entity.working_robot.wr_working_status import WrWorkingStatus
from src.production.base.coordinates import Coordinates


@dataclass
class WorkingRobot:
    identification_number: int
    size: Coordinates
    driving_speed: int
    product_transfer_rate: int
    working_status: WrWorkingStatus

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"WR: {self.identification_number}"
