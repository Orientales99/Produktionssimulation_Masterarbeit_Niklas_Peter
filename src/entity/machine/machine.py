from dataclasses import dataclass, field

from src.constant.constant import MachineQuality
from src.entity.machine.Process_material import ProcessMaterial
from src.entity.machine.machine_working_status import MachineWorkingStatus
from src.entity.machine.processing_order import ProcessingOrder
from src.production.base.coordinates import Coordinates
from src.entity.machine.machine_storage import MachineStorage
from src.order_data.production_material import ProductionMaterial


@dataclass
class Machine:
    machine_type: int
    identification_number: int
    machine_quality: MachineQuality
    driving_speed: int
    working_speed: int
    working_speed_deviation: float
    size: Coordinates
    machine_storage: MachineStorage
    working_status: MachineWorkingStatus
    setting_up_time: float  # Rüstzeit

    processing_list: list[ProcessingOrder] = field(
        default_factory=list)  # default: empty | list (Order, step of the process)
    process_material_list: list[ProcessMaterial] = field(
        default_factory=list)  # default: empty | list (ProductionMaterial, necessary quantity)
    processing_list_queue_length: float = 0

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"Ma: {self.machine_type}, {self.identification_number}"

    @property
    def producing_efficiency_factor(self) -> float:
        if self.machine_quality == MachineQuality.NEW_MACHINE:
            return float(0.8)
        return float(1)

