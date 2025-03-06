from collections import defaultdict

from src.data.service_order import ServiceOrder
from src.data.service_entity import ServiceEntity
from src.data.service_starting_condition import ServiceStartingConditions
from src.data.cell import Cell
from src.data.coordinates import Coordinates
from src.data.sink import Sink
from src.data.source import Source


class Production:
    production_layout: list[list[Cell]] = []
    service_order = ServiceOrder()
    service_entity = ServiceEntity()
    service_starting_conditions = ServiceStartingConditions()
    source_coordinates: Coordinates
    sink_coordinates: Coordinates
    wr_list = []
    tr_list = []
    machine_list = []
    max_coordinate: Coordinates

    def __init__(self):
        self.get_data_from_service_order()

    def create_production(self):
        self.build_layout()
        self.set_source_in_production_layout()
        self.set_sink_in_production_layout()

    def set_entities(self):

        self.get_working_robot_placed_in_production()
        self.get_transport_robot_placed_in_production()
        self.get_every_machine_placed_in_production()

    def get_data_from_service_order(self):
        self.wr_list = self.service_entity.generate_wr_list()
        self.tr_list = self.service_entity.generate_tr_list()
        self.machine_list = self.service_entity.generate_machine_list()
        self.max_coordinate = self.service_starting_conditions.set_max_coordinates_for_production_layout()

    def build_layout(self):
        """Forms a list in a list (production_layout), which represents a coordinate system consisting of the class
        Cell"""
        for y in reversed(range(0, self.max_coordinate.y)):
            row: list[Cell] = []
            for x in range(0, self.max_coordinate.x):
                cell = Cell(Coordinates(x, y), None)
                row.append(cell)
            self.production_layout.append(row)

    def set_source_in_production_layout(self):
        self.source_coordinates = Coordinates(0, int(self.max_coordinate.y / 2))
        cell = self.get_cell(self.source_coordinates)
        cell.placed_entity = Source(0, 0, 0)

    def set_sink_in_production_layout(self):
        self.sink_coordinates = Coordinates(int(self.max_coordinate.x - 1), int(self.max_coordinate.y / 2))
        cell = self.get_cell(self.sink_coordinates)
        cell.placed_entity = Sink(0, 0, 0)

    def get_working_robot_placed_in_production(self):
        number_of_working_robots = len(self.wr_list)
        avoiding_collision_parameter = 1
        for i in range(0, number_of_working_robots):
            while True:
                new_coordinates_working_robot = Coordinates(self.source_coordinates.x,
                                                            self.source_coordinates.y + self.wr_list[
                                                                i].robot_size.y + 1 + avoiding_collision_parameter)
                new_cell = self.get_cell(new_coordinates_working_robot)
                checked_free_area_list = self.check_area_of_cells_is_free(new_cell, self.wr_list[i].robot_size)
                checked_free_area_list_length = len(checked_free_area_list)
                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = self.wr_list[i]
                    break
                else:
                    avoiding_collision_parameter += self.wr_list[i].robot_size.y + 1

    def get_transport_robot_placed_in_production(self, ):
        number_of_transport_robots = len(self.tr_list)
        avoiding_collision_parameter = 1
        for i in range(0, number_of_transport_robots):
            while True:
                new_coordinates_transport_robot = Coordinates(self.source_coordinates.x,
                                                              self.source_coordinates.y - avoiding_collision_parameter)
                new_cell = self.get_cell(new_coordinates_transport_robot)
                checked_free_area_list = self.check_area_of_cells_is_free(new_cell, self.tr_list[i].robot_size)
                checked_free_area_list_length = len(checked_free_area_list)
                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = self.tr_list[i]
                    break
                else:
                    avoiding_collision_parameter += self.tr_list[i].robot_size.y + 1

    def get_max_length_of_tr_or_wr(self):
        """Finds max. length of size.x or size.y from TR and WR"""
        max_robot_size = 0
        for x in range(0, len(self.wr_list)):
            if max_robot_size < self.wr_list[x].robot_size.x:
                max_robot_size = self.wr_list[x].robot_size.x
            if max_robot_size < self.wr_list[x].robot_size.y:
                max_robot_size = self.wr_list[x].robot_size.y

        for y in range(0, len(self.tr_list)):
            if max_robot_size < self.tr_list[y].robot_size.x:
                max_robot_size = self.tr_list[y].robot_size.x
            if max_robot_size < self.tr_list[y].robot_size.y:
                max_robot_size = self.tr_list[y].robot_size.y
        return max_robot_size

    def safe_space_for_placing_machines_in_production(self) -> list:
        safed_cells_for_machine_list = []
        pass

    def get_size_and_number_of_machine(self):
        """Get a list of space per machine and the quantity of the required machine_space"""
        coordinate_count = defaultdict(
            int)  # int: The default value (in this example: Coordinate) for non-existent keys is 0
        for x in range(0, len(self.machine_list)):
            coordinates = (int(self.machine_list[x].machine_size.x), int(self.machine_list[x].machine_size.y))
            coordinate_count[coordinates] += 1
        coordinate_list = [(Coordinates(coord[0], coord[1]), int(count)) for coord, count in coordinate_count.items()]
        return coordinate_list

    def get_every_machine_placed_in_production(self):
        machine_list_static = self.get_machine_list_static()
        machine_list_flexible = self.get_machine_list_flexible()
        self.get_static_machine_placed_in_production(machine_list_static)
        self.get_flexible_machine_placed_in_production(machine_list_flexible)

    def get_machine_list_static(self):
        return [machine for machine in self.machine_list if int(machine.driving_speed) == 0]

    def get_machine_list_flexible(self) -> list:
        return [machine for machine in self.machine_list if int(machine.driving_speed) != 0]

    def get_static_machine_placed_in_production(self, machine_list_static: list):
        """sets static machine in the production_layout. Alternate between one machine above source and one below. All
        machines of one type are positioned on the same x-Axis. The next machine_type [i] is positions on the left side from the machine_type [i-1]"""
        number_of_machine = len(machine_list_static)
        avoiding_collision_parameter_x = 0

        space_between_machine = (
                self.get_max_length_of_tr_or_wr() * 2)  # *2 because two robots should drive between machines simultaneously
        y_start = self.sink_coordinates.y + int(
            (machine_list_static[0].machine_size.y) / 2) + 1
        y_parameter = y_start
        y_upwards = y_start
        y_downwards = y_start
        collusion_parameter = machine_list_static[0].machine_size.y

        for i in range(0, number_of_machine):
            while True:
                new_coordinates = Coordinates(
                    self.sink_coordinates.x - 5 - space_between_machine - avoiding_collision_parameter_x -
                    machine_list_static[
                        i].machine_size.x,
                    y_parameter)
                new_cell = self.get_cell(new_coordinates)

                checked_free_area_list = self.check_area_of_cells_is_free(new_cell, machine_list_static[i].machine_size)
                checked_free_area_list_length = len(checked_free_area_list)

                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = machine_list_static[i]
                    break
                else:
                    if machine_list_static[i].machine_type == machine_list_static[i - 1].machine_type or \
                            machine_list_static[
                                i].machine_type == machine_list_static[0].machine_type:
                        if machine_list_static[i].identification_number % 2 != 0:
                            y_upwards += machine_list_static[i].machine_size.y + space_between_machine + 3
                            y_parameter = y_upwards
                        elif machine_list_static[i].identification_number % 2 == 0:
                            y_downwards -= collusion_parameter + space_between_machine + 3
                            collusion_parameter = machine_list_static[
                                i].machine_size.y
                            y_parameter = y_downwards
                        else:
                            raise Exception(
                                'An error occurred when initialising static machines in the production_layout.')

                    else:
                        avoiding_collision_parameter_x += machine_list_static[
                                                              i].machine_size.x + space_between_machine + 1
                        y_parameter = y_start
                        y_upwards = y_start
                        y_downwards = y_start

    def get_flexible_machine_placed_in_production(self, machine_list_flexible: list):
        """sets flexible machine in the production_layout. Alternate between one machine above source and one below. All
        machines of one type are positioned one behind the other (x-axis)"""
        number_of_machine = len(machine_list_flexible)
        avoiding_collision_parameter_x = 0

        space_between_machine = (
                self.get_max_length_of_tr_or_wr() * 2)  # *2 because two robots should drive between machines simultaneously
        y_start = self.source_coordinates.y + int(
            (machine_list_flexible[0].machine_size.y) / 2) + 1
        y_parameter = y_start
        y_upwards = y_start
        y_downwards = y_start
        collusion_parameter = machine_list_flexible[0].machine_size.y

        for i in range(0, number_of_machine):
            while True:
                new_coordinates = Coordinates(
                    self.source_coordinates.x + 5 + space_between_machine + avoiding_collision_parameter_x,
                    y_parameter)
                new_cell = self.get_cell(new_coordinates)

                checked_free_area_list = self.check_area_of_cells_is_free(new_cell,
                                                                          machine_list_flexible[i].machine_size)
                checked_free_area_list_length = len(checked_free_area_list)

                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = machine_list_flexible[i]
                    break
                else:
                    if machine_list_flexible[i].machine_type == machine_list_flexible[i - 1].machine_type or \
                            machine_list_flexible[
                                i].machine_type == machine_list_flexible[0].machine_type:
                        avoiding_collision_parameter_x += machine_list_flexible[
                                                              i].machine_size.x + space_between_machine + 1
                    else:
                        if machine_list_flexible[i].machine_type % 2 != 0:
                            y_upwards += machine_list_flexible[i].machine_size.y + space_between_machine + 3
                            y_parameter = y_upwards
                            avoiding_collision_parameter_x = 0
                        elif machine_list_flexible[i].machine_type % 2 == 0:
                            y_downwards -= collusion_parameter + space_between_machine + 3
                            collusion_parameter = machine_list_flexible[
                                i].machine_size.y
                            y_parameter = y_downwards
                            avoiding_collision_parameter_x = 0
                        else:
                            raise Exception(
                                'An error occurred when initialising flexible machines in the production_layout.')

    def check_area_of_cells_is_free(self, cell: Cell, free_area_size: Coordinates) -> list:
        """get a cell and is checking if the area downward and to right is free; if free -> return list with free cells; if not free -> if not free -> return empty list"""
        list_of_checked_cells = []
        y_range_min = cell.cell_coordinates.y - free_area_size.y
        y_range_max = cell.cell_coordinates.y
        x_range_min = cell.cell_coordinates.x
        x_range_max = cell.cell_coordinates.x + free_area_size.x

        for y in range(y_range_min, y_range_max):
            for x in range(x_range_min, x_range_max):
                checked_cell = self.get_cell(Coordinates(x, y))
                if self.check_cell_is_free(checked_cell) is False:
                    list_of_checked_cells = []
                    return list_of_checked_cells
                else:
                    list_of_checked_cells.append(checked_cell)
        return list_of_checked_cells

    def check_cell_is_free(self, cell: Cell) -> bool:
        if cell.placed_entity is None:
            return True
        else:
            return False

    def get_cell(self, coordinates: Coordinates) -> Cell:
        return self.production_layout[len(self.production_layout) - 1 - coordinates.y][coordinates.x]

    def coordinates_in_layout(self, testing_coordinates: Coordinates) -> bool:
        """Is checking if the coordinates are in the production_layout"""
        if testing_coordinates.x >= 0 or testing_coordinates.x < self.max_coordinate.x or testing_coordinates.y >= 0 or testing_coordinates.y < self.max_coordinate.y:
            return True
        else:
            return False
