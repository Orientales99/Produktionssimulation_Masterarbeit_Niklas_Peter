from src.entity.working_robot import WorkingRobot
from src.order_data.order import Order
from src.production.base.coordinates import Coordinates
from src.entity.machine import Machine
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.path_finding import PathFinding
from src.production.base.cell import Cell
from src.production.visualisation.production_visualisation import ProductionVisualisation


class WorkingRobotManager:
    manufacturing_plan: ManufacturingPlan
    path_finding: PathFinding
    sorted_list_of_processes: list[tuple[Machine, Order, int]] = []
    list_wr_in_production: list[WorkingRobot] = []
    list_driving_wr: list[WorkingRobot]
    dict_of_working_wr: dict[str, list[Cell]] = {}  # str= wr.identification_str
    list_wr_working_on_machine: list[WorkingRobot]
    waiting_time: int

    def __init__(self, manufacturing_plan: ManufacturingPlan, path_finding: PathFinding):
        self.manufacturing_plan = manufacturing_plan
        self.v = ProductionVisualisation(self.manufacturing_plan.production)
        self.path_finding = path_finding
        self.list_wr_working_on_machine = []
        self.list_driving_wr = []

        self.list_wr_in_production = self.manufacturing_plan.production.wr_list

        self.waiting_time = self.list_wr_in_production[0].working_status.waiting_time_on_path

    def start_working_robot_manager(self):
        self.sort_process_order_list_for_wr()
        self.get_next_working_location_for_order()
        self.get_path_for_wr()

    def get_path_for_wr(self):
        for wr in self.list_wr_in_production:
            if wr.working_status.driving_destination_work_on_machine is not None:
                path_line_list = self.path_finding.get_path_for_entity(wr, wr.working_status.driving_destination_work_on_machine)
                wr.working_status.driving_route_work_on_machine = path_line_list
                wr.working_status.driving_to_new_location = True
                self.list_driving_wr.append(wr)

    def wr_drive_through_production(self):
        """moving the wr one step further through the production. When a wr cannot move it's waiting for waiting_time
        period until in calculates a new path"""

        for wr in self.list_driving_wr:
            if isinstance(wr.working_status.driving_route_work_on_machine, Exception):
                self.v.visualize_layout()
                print(f'{wr.identification_str}:{self.path_finding.get_start_cell_from_entity(wr)}, {wr.working_status.driving_route_work_on_machine}')
            else:

                if wr.working_status.driving_to_new_location is True and len(wr.working_status.driving_route_work_on_machine) != 0:

                    start_cell = self.path_finding.get_start_cell_from_entity(wr)

                    if self.path_finding.entity_movement.move_entity_one_step(start_cell, wr,
                                                                              wr.working_status.driving_route_work_on_machine[0]) is True:
                        wr.working_status.driving_route_work_on_machine.pop(0)
                        wr.working_status.waiting_time_on_path = self.waiting_time
                    else:
                        wr.working_status.waiting_time_on_path -= 1
                        if wr.working_status.waiting_time_on_path == 0:
                            path_line_list = self.path_finding.get_path_for_entity(wr,
                                                                                   wr.working_status.driving_destination_work_on_machine)
                            wr.working_status.driving_route_work_on_machine = path_line_list

                elif len(wr.working_status.driving_route_work_on_machine) == 0 and wr.working_status.driving_to_new_location is True \
                        and wr.working_status.working_for_machine is not None:
                    if wr not in self.list_wr_working_on_machine:
                        self.wr_arrived_on_destination(wr)

    def wr_arrived_on_destination(self, working_robot):

        machine_identification_str = working_robot.working_status.working_for_machine.identification_str

        self.change__working_robot_on_machine_status(machine_identification_str, True)

        cell_list_wr = self.manufacturing_plan.production.entities_located[working_robot.identification_str]

        for cell in cell_list_wr:
            cell.placed_entity = None
        self.dict_of_working_wr[working_robot.identification_str] = cell_list_wr
        self.list_driving_wr.remove(working_robot)
        self.list_wr_working_on_machine.append(working_robot)


    def change__working_robot_on_machine_status(self, machine_identification_str: str, status: bool):
        cell_list_machine = self.manufacturing_plan.production.entities_located[machine_identification_str]
        for cell in cell_list_machine:
            cell.placed_entity.working_robot_on_machine = status

    def sort_process_order_list_for_wr(self):
        list_of_processes_for_every_machine = self.manufacturing_plan.process_list_for_every_machine

        self.sorted_list_of_processes = sorted(list_of_processes_for_every_machine,
                                               key=lambda x: x[1].daily_manufacturing_sequence, reverse=False)
        self.sorted_list_of_processes = sorted(list_of_processes_for_every_machine, key=lambda x: x[1].priority,
                                               reverse=False)

    def get_next_working_location_for_order(self):
        """process_order = (Machine, Order, int) int is an indicator for the process_step in order"""
        for wr in self.list_wr_in_production:
            if wr.working_status.waiting_for_order is True:
                sorted_list_of_processes_local = self.sorted_list_of_processes[:]
                for process_order in sorted_list_of_processes_local:

                    if process_order[0].waiting_for_arriving_of_wr is False and process_order[
                        0].working_robot_on_machine is False:
                        wr.working_status.waiting_for_order = False
                        process_order[0].waiting_for_arriving_of_wr = True
                        wr.working_status.working_for_machine = process_order[0]
                        wr.working_status.driving_destination_work_on_machine = self.calculate_coordinates_of_new_driving_destination(
                            process_order[0], wr)

                        self.sorted_list_of_processes.remove(process_order)
                        break

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

    def get_driving_speed_per_cell(self):
        return int(self.list_wr_in_production[0].driving_speed)
