from dataclasses import dataclass

from src.process_logic.manufacturing_plan import ManufacturingPlan


@dataclass
class TransportRobotManager:
    manufacturing_plan = ManufacturingPlan()
    material_requirements_per_machine = manufacturing_plan.get_required_material_for_every_machine()


