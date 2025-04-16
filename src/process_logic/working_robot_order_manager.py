import random
from collections import Counter

from src.constant.constant import MachineWorkingRobotStatus
from src.entity.machine.machine import Machine
from src.entity.machine.processing_order import ProcessingOrder
from src.entity.source import Source
from src.entity.working_robot.working_robot import WorkingRobot
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.path_finding import PathFinding
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates


class WorkingRobotManager:
    manufacturing_plan: ManufacturingPlan
    path_finding: PathFinding
    sorted_list_of_processes: list[(Machine, ProcessingOrder)] = []

    def __init__(self, manufacturing_plan: ManufacturingPlan, path_finding: PathFinding):
        self.manufacturing_plan = manufacturing_plan
        self.path_finding = path_finding

        self.wr_list = self.manufacturing_plan.production.wr_list
        self.entities_located_after_init = self.manufacturing_plan.production.entities_init_located

        self.waiting_time = self.wr_list[0].working_status.waiting_time_on_path

    def create_working_request_list_from_machines(self):
        pass

    def sort_process_order_list_for_wr(self):
        """Sort list [machine, processing_order(Order, step_of_the_process_priority)].
         1. priority
         2. step of the process
         3. daily manufacturing_sequence
         """
        list_of_processes_for_every_machine = self.manufacturing_plan.process_list_for_every_machine[:]

        self.sorted_list_of_processes = sorted(
            list_of_processes_for_every_machine,
            key=lambda x: (x[1].order.priority.value,
                           - x[1].step_of_the_process,
                           x[1].order.daily_manufacturing_sequence,
                           )
        )

    def get_waiting_location_for_wr(self, wr: WorkingRobot):
        source_coordinates = self.manufacturing_plan.production.source_coordinates
        source_cell = self.manufacturing_plan.production.get_cell(source_coordinates)
        destination = source_cell.placed_entity

        if self.set_driving_to_waiting_station_parameter_for_wr(wr, destination):
            return True
        return False

    def set_driving_to_waiting_station_parameter_for_wr(self, wr: WorkingRobot, destination: Source) -> bool:
        driving_destination_coordinates = self.path_finding.get_init_coordinates_from_entity(wr)
        driving_route = self.path_finding.get_path_for_entity(wr, driving_destination_coordinates)

        if isinstance(driving_route, list):
            wr.working_status.driving_destination_coordinates = driving_destination_coordinates
            wr.working_status.driving_route = driving_route
            return True
        return False

    def get_next_working_location_for_order(self, wr: WorkingRobot) -> bool:
        for process_order in self.sorted_list_of_processes[:]:
            machine = process_order[0]

            if machine.working_status.working_robot_status == MachineWorkingRobotStatus.NO_WR or \
                    machine.working_status.working_robot_status == MachineWorkingRobotStatus.WR_LEAVING:
                wr.working_status.working_for_machine = machine

                wr.working_status.driving_destination_coordinates = \
                    self.calculate_coordinates_of_new_driving_destination(machine, wr)

                machine.working_status.working_robot_status = MachineWorkingRobotStatus.WAITING_WR
                self.sorted_list_of_processes.remove(process_order)
                return True

        return False

    def calculate_coordinates_of_new_driving_destination(self, destination_machine: Machine,
                                                         wr: WorkingRobot) -> Coordinates:
        """Calculate the destination cell for the wr. It is the cell in the upper right corner of the WR"""

        location_machine = self.manufacturing_plan.production.entities_located[destination_machine.identification_str]
        vertical_edges_machine = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(location_machine)
        horizontal_edges_machine = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
            location_machine)

        location_wr = self.manufacturing_plan.production.entities_located[wr.identification_str]
        vertical_edges_wr = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(location_wr)
        horizontal_edges_wr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
            location_wr)

        destination_coordinates = Coordinates(
            horizontal_edges_machine[0] - (horizontal_edges_wr[1] - horizontal_edges_wr[0] + 2),
            vertical_edges_machine[1] -
            (vertical_edges_machine[1] - vertical_edges_machine[0]) +
            (vertical_edges_wr[1] - vertical_edges_wr[0] + 2))

        return destination_coordinates

    def get_path_for_wr(self, wr: WorkingRobot) -> bool:
        """Calculate and safe the path for wr to the next destination.
        Return True -> is correctly calculated.
        Return False -> the path couldn't get calculated."""
        destination_coordinates = wr.working_status.driving_destination_coordinates
        path_line_list = self.path_finding.get_path_for_entity(wr,
                                                               destination_coordinates)
        if isinstance(path_line_list, list):
            wr.working_status.driving_route = path_line_list
            return True
        else:
            return False

    def drive_wr_one_step_trough_production(self, wr: WorkingRobot) -> bool:
        """moving the wr one step further through the production to destination.
           When a wr cannot move it's waiting for waiting_time period until in calculates a new path.
           Returns True on the right place."""

        start_cell = self.path_finding.get_start_cell_from_entity(wr)
        path = wr.working_status.driving_route

        if isinstance(path, Exception):
            path = self.path_finding.get_path_for_entity(wr, wr.working_status.driving_destination_coordinates)
            wr.working_status.driving_route = path
            return False

        if len(path) > 0:
            if self.path_finding.entity_movement.move_entity_one_step(start_cell, wr, path[0]) is True:
                wr.working_status.driving_route.pop(0)
                wr.working_status.waiting_time_on_path = self.waiting_time

            else:
                wr.working_status.waiting_time_on_path -= 1
                if wr.working_status.waiting_time_on_path == 0:
                    path = self.path_finding.get_path_for_entity(wr, wr.working_status.driving_destination_coordinates)
                    wr.working_status.driving_route = path
                    wr.working_status.waiting_time_on_path = random.randint(1, 10)

        if isinstance(path, Exception):
            path = self.path_finding.get_path_for_entity(wr, wr.working_status.driving_destination_coordinates)
            wr.working_status.driving_route = path
            return False

        if len(wr.working_status.driving_route) == 0:
            return True

        return False

    def wr_driving_in_machine(self, wr: WorkingRobot):
        """Cells with the placed_entity of wr will be changed to None. The Cell coordinates are saved in
        wr.working_status.last_placement_in_production: list[Cell]."""

        machine = wr.working_status.working_for_machine
        cell_list_wr = self.manufacturing_plan.production.entities_located[wr.identification_str]

        for cell in cell_list_wr:
            cell.placed_entity = None

        machine.working_status.working_robot_status = MachineWorkingRobotStatus.WR_PRESENT

        wr.working_status.last_placement_in_production = cell_list_wr

    def wr_driving_off_machine(self, wr: WorkingRobot) -> bool:
        """If wr can drive off machine -> Return: True
           If wr cannot drive off machine -> Return: False"""

        cell_list = wr.working_status.last_placement_in_production

        if self.check_cell_list_is_none(cell_list):
            for cell in cell_list:
                cell.placed_entity = wr
            return True

        return False

    def check_cell_list_is_none(self, cell_list: list[Cell]) -> bool:
        """if every cell.placed_entity in this list is none -> Return: True, otherwise Return: False"""

        for cell in cell_list:
            if cell.placed_entity is not None:
                return False
        return True

    def check_if_tr_is_on_waiting_place(self, wr: WorkingRobot) -> bool:
        """ Checks if the WR is in the right waiting position. The waiting position is the place where the
        WR was initiated."""

        coords_1 = [(cell.cell_coordinates.x, cell.cell_coordinates.y) for cell in
                    self.entities_located_after_init[wr.identification_str]]
        coords_2 = [(cell.cell_coordinates.x, cell.cell_coordinates.y) for cell in
                    self.manufacturing_plan.production.entities_located[wr.identification_str]]

        if Counter(coords_1) == Counter(coords_2):
            return True
        else:
            return False

    def get_driving_speed_per_cell(self):
        return int(self.wr_list[0].driving_speed)
