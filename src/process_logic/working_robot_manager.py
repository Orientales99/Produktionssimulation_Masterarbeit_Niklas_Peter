from dataclasses import dataclass

from src.data.production import Production


@dataclass
class WorkingRobotManager:
    production = Production()
    process_order_of_wr_dict = {}

    def get_process_order(self):

        machine_type_list = self.production.service_entity.get_quantity_per_machine_types_list()
        for machine_type, number_of_machines_in_production in machine_type_list:
            for identification_number in range(1, number_of_machines_in_production + 1):
                
