from dataclasses import dataclass

from src.production.base.coordinates import Coordinates
from src.entity.entity_working_status import EntityWorkingStatus


@dataclass
class WorkingRobot:
    identification_number: int
    size: Coordinates
    driving_speed: int
    product_transfer_rate: int
    working_status: EntityWorkingStatus

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"WR: {self.identification_number}"
