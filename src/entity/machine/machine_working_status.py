from dataclasses import dataclass

from src.constant.constant import MachineProcessStatus, MachineWorkingRobotStatus
from src.order_data.production_material import ProductionMaterial


@dataclass
class MachineWorkingStatus:
    process_status: MachineProcessStatus
    working_robot_status: MachineWorkingRobotStatus
    working_on_status: bool

    producing_production_material: ProductionMaterial | None
    waiting_for_arriving_of_tr: bool
