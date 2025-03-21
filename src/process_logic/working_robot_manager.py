from dataclasses import dataclass

from src.data.production import Production
from src.process_logic.manufacturing_plan import ManufacturingPlan


@dataclass
class WorkingRobotManager:
    production = Production()
    manufacturing_plan = ManufacturingPlan()
    process_order_of_wr_dict = {}



    def get_every_process_order_from_machines(self):
        number_of_init_wr = self.production.service_entity.get_quantity_of_wr()
        list_of_wr_identification_str = self.get_list_of_all_wr_identification_str()
        list_of_machine_identification_str = self.manufacturing_plan.get_list_machine_identification_str()
        entity_located = self.production.entities_located

        for machine_str in list_of_machine_identification_str:
            machine_cell = entity_located[machine_str][1]
            print(machine_cell)

        #for x in range(1, number_of_init_wr + 1):
        #
        #    self.process_order_of_wr_dict[list_of_wr_identification_str[x]]
        #
        pass

    def get_list_of_all_wr_identification_str(self) -> list[str]:
        number_of_wr = self.production.service_entity.get_quantity_of_wr()
        every_wr_identification_str_list = []

        for x in range(1, number_of_wr + 1):
            identification_str = f"WR: {x}"
            every_wr_identification_str_list.append(identification_str)

        return every_wr_identification_str_list
