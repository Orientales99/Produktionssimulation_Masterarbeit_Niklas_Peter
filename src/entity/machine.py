from dataclasses import dataclass, field

from src.constant.constant import MachineQuality
from src.entity.required_material import RequiredMaterial
from src.order_data.order import Order
from src.order_data.product import Product
from src.production.base.coordinates import Coordinates
from src.entity.machine_storage import MachineStorage
from src.order_data.production_material import ProductionMaterial


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
    setting_up_time: float  # Rüstzeit

    processing_list: list[(Order, int)] = field(
        default_factory=list)  # default: empty | list (Order, step of the process)
    required_material_list: list[RequiredMaterial] = field(
        default_factory=list)  # default: empty | list (ProductionMaterial, necessary quantity)
    processing_list_queue_length: float = 0
    waiting_for_arriving_of_wr: bool = False

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"Ma: {self.machine_type}, {self.identification_number}"


