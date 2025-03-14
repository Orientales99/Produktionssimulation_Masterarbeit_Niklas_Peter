from dataclasses import dataclass

from src.data.constant import MachineQuality
from src.data.product import Product
from src.data.coordinates import Coordinates
from src.data.machine_storage import MachineStorage


@dataclass
class Machine:
    machine_type: int
    identification_number: int
    machine_quality: MachineQuality
    driving_speed: int
    working_speed: int
    size: Coordinates
    machine_storage: MachineStorage
    working_robot_on_machine: bool
    producing_product: Product | None
    setting_up_time: int  # Rüstzeit

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"Ma: {self.machine_type}, {self.identification_number}"
