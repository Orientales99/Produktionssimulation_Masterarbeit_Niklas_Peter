from datetime import date

from src.entity.machine import Machine
from src.order_data.production_material import ProductionMaterial
from src.process_logic.manufacturing_plan import ManufacturingPlan


class MachineExecution:
    manufacturing_plan: ManufacturingPlan
    machine_list: list[Machine]
    required_material: dict[str, list[
        (ProductionMaterial, int)]]  # dict[machine.identification_str, list[tuple(ProductionMaterial, Quantity)]
    list_full_store_after_process = list[Machine]


    def __init__(self, manufacturing_plan):
        self.manufacturing_plan = manufacturing_plan
        self.machine_list = self.manufacturing_plan.production.machine_list
        self.required_material = self.manufacturing_plan.required_materials_for_every_machine
        self.list_full_store_after_process = []
        self.material_transport_request_list = []

    def create_tr_process_order_list(self):

        pass

    def check_any_machine_store_after_process_full(self):
        for machine in self.machine_list:
            if len(machine.machine_storage.storage_after_process.items) >= machine.machine_storage.storage_after_process.capacity:
                self.list_full_store_after_process.append(machine)

    def check_for_starting_machine_process(self):
        """Checking if the machine can start the production of production"""
        for machine in self.machine_list:
            if machine not in self.list_full_store_after_process:
                if machine.processing_list > 0:
                    if machine.working_robot_on_machine is True or machine.waiting_for_arriving_of_wr is True:
                        order, step = machine.processing_list[0]
                        required_material = f'required_product_type_step_{step}'
                        if required_material in machine.machine_storage.storage_before_process.items:
                            self.start_process(machine)


                        else:  # request_tr
                            pass
                    else:  # request wr
                        pass
            else:  # check for new orders
                pass

    def start_process_of_machine(self, machine):
        pass

