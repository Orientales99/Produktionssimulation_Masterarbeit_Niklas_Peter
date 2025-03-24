from dataclasses import dataclass, field

from src.data.coordinates import Coordinates
from src.data.production import Production
from src.entity_classes.machine import Machine
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.path_finding import PathFinding


@dataclass
class WorkingRobotManager:
    manufacturing_plan: ManufacturingPlan = field(init=False)
    path_finding: PathFinding = field(init=False)
    process_order_of_wr_dict: dict = field(default_factory=dict)
    sorted_list_of_processes: list = field(default_factory=list)
    list_wr_in_production: list = field(default_factory=list)

    def __init__(self, manufacturing_plan: ManufacturingPlan, path_finding: PathFinding):
        self.manufacturing_plan = manufacturing_plan
        self.path_finding = path_finding
        self.get_list_of_all_wr()

    def start_working_robot_manager(self):
        self.sort_process_order_list_for_wr()
        self.get_next_working_location_for_order()
        for wr in self.list_wr_in_production:
            path_line_list = self.path_finding.get_path_for_entity(wr, wr.working_status.driving_destination)
            print(path_line_list)

    def sort_process_order_list_for_wr(self):
        list_of_processes_for_every_machine = self.manufacturing_plan.process_list_for_every_machine

        self.sorted_list_of_processes = sorted(list_of_processes_for_every_machine,
                                               key=lambda x: x[1].daily_manufacturing_sequence, reverse=False)
        self.sorted_list_of_processes = sorted(list_of_processes_for_every_machine, key=lambda x: x[1].priority,
                                               reverse=False)

    def get_list_of_all_wr(self) -> list[str]:
        number_of_wr = self.manufacturing_plan.production.service_entity.get_quantity_of_wr()
        self.list_wr_in_production = []

        for x in range(1, number_of_wr + 1):
            identification_str = f"WR: {x}"

            cell = self.manufacturing_plan.production.find_cell_in_production_layout(
                self.manufacturing_plan.production.entities_located[identification_str][1])
            self.list_wr_in_production.append(cell.placed_entity)

        return self.list_wr_in_production

    def get_next_working_location_for_order(self):
        for wr in self.list_wr_in_production:
            if wr.working_status.waiting_for_order is True:
                process_order = self.sorted_list_of_processes[0]

                if process_order[0].waiting_for_arriving_of_wr is False and process_order[
                    0].working_robot_on_machine is False:
                    wr.working_status.waiting_for_order = False
                    process_order[0].waiting_for_arriving_of_wr = True
                    wr.working_status.driving_destination = self.calculate_coordinates_of_new_driving_destination(
                        process_order[0], wr)
                    self.sorted_list_of_processes.remove(process_order)

            print(wr.identification_str)
            print(process_order[1])
            print(wr.working_status.driving_destination)

    def calculate_coordinates_of_new_driving_destination(self, destination_machine: Machine,
                                                         working_robot) -> Coordinates:
        """Calculate the destination cell for the wr. It is the cell in the upper right corner of the WR"""

        location_machine = self.manufacturing_plan.production.entities_located[destination_machine.identification_str]
        vertical_edges_machine = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(location_machine)
        horizontal_edges_machine = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
            location_machine)

        location_wr = self.manufacturing_plan.production.entities_located[working_robot.identification_str]
        vertical_edges_wr = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(location_wr)
        horizontal_edges_wr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
            location_wr)

        destination_coordinates = Coordinates(
            horizontal_edges_machine[0] - (horizontal_edges_wr[1] - horizontal_edges_wr[0] + 2),
            vertical_edges_machine[1] -
            (vertical_edges_machine[1] - vertical_edges_machine[0]) +
            (vertical_edges_wr[1] - vertical_edges_wr[0] + 2))

        return destination_coordinates
