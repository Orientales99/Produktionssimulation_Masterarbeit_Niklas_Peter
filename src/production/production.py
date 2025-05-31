import math
import simpy

from collections import defaultdict
from simpy import Store

from src.entity.intermediate_store import IntermediateStore
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.provide_input_data.entity_service import EntityService
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot


class Production:
    production_layout: list[list[Cell]] = []

    service_starting_conditions = StartingConditionsService
    source_coordinates: Coordinates
    sink_coordinates: Coordinates
    wr_list: list[WorkingRobot]
    entities_located: {str, list[Cell]}  # {entity.identification_str, list[Cell]}
    entities_init_located: dict[str, list[Cell]]  # {entity.identification_str, list[Cell]} position of initialisation
    tr_list: list[TransportRobot]
    machine_list: list[Machine]
    intermediate_store_list: list[IntermediateStore]

    max_coordinate: Coordinates

    def __init__(self, simulation_environment: simpy.Environment,
                 service_starting_conditions: StartingConditionsService):
        self.env = simulation_environment
        self.service_entity = EntityService(simulation_environment)
        self.service_starting_conditions = service_starting_conditions
        self.wr_list = []
        self.entities_located = {}
        self.entities_init_located = {}
        self.tr_list = []
        self.machine_list = []
        self.intermediate_store_list = []

        self.get_data_from_service_order()

    def create_production(self):
        self.create_production_layout()
        self.set_entities()

    def create_production_layout(self):
        self.build_layout()
        self.set_source_in_production_layout()
        self.set_sink_in_production_layout()

    def set_entities(self):
        self.get_working_robot_placed_in_production()
        self.get_transport_robot_placed_in_production()
        self.get_every_machine_placed_in_production()
        self.get_intermediate_store_placed_in_production()

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
        """Places the source at the center of the left side of the production layout."""
        self.source_coordinates = Coordinates(0, int(self.max_coordinate.y / 2))
        cell = self.get_cell(self.source_coordinates)
        cell.placed_entity = Source(0, 0, 0)

    def set_sink_in_production_layout(self):
        """Places the sink at the center of the right side of the production layout."""
        self.sink_coordinates = Coordinates(int(self.max_coordinate.x - 1), int(self.max_coordinate.y / 2))
        cell = self.get_cell(self.sink_coordinates)
        cell.placed_entity = Sink(Store(self.env), [])

    def get_working_robot_placed_in_production(self):
        """Places working robots in the production layout and stores their locations in a dictionary"""

        number_of_working_robots = len(self.wr_list)
        avoiding_collision_parameter = 1
        for i in range(0, number_of_working_robots):
            while True:
                location_list = []
                new_coordinates_working_robot = Coordinates(self.source_coordinates.x,
                                                            self.source_coordinates.y + self.wr_list[
                                                                i].size.y + 2 + avoiding_collision_parameter)
                new_cell = self.get_cell(new_coordinates_working_robot)
                checked_free_area_list = self.check_area_of_cells_is_free_for_entity(new_cell,
                                                                                     self.wr_list[i].size,
                                                                                     None)
                checked_free_area_list_length = len(checked_free_area_list)
                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = self.wr_list[i]
                        location_list.append(new_cell)
                    break
                else:
                    avoiding_collision_parameter += self.wr_list[i].size.y + 2
            self.entities_located[self.wr_list[i].identification_str] = location_list
            self.entities_init_located[self.wr_list[i].identification_str] = location_list

    def get_transport_robot_placed_in_production(self):
        """Places transport robots in the production layout and stores their locations in a dictionary"""

        number_of_transport_robots = len(self.tr_list)
        avoiding_collision_parameter = 1
        for i in range(0, number_of_transport_robots):
            while True:
                location_list = []
                new_coordinates_transport_robot = Coordinates(self.source_coordinates.x,
                                                              self.source_coordinates.y - avoiding_collision_parameter)
                new_cell = self.get_cell(new_coordinates_transport_robot)
                checked_free_area_list = self.check_area_of_cells_is_free_for_entity(new_cell,
                                                                                     self.tr_list[i].size,
                                                                                     None)
                checked_free_area_list_length = len(checked_free_area_list)
                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = self.tr_list[i]
                        location_list.append(new_cell)
                    break
                else:
                    avoiding_collision_parameter += self.tr_list[i].size.y + 2
            self.entities_located[self.tr_list[i].identification_str] = location_list
            self.entities_init_located[self.tr_list[i].identification_str] = location_list

    def get_max_length_of_tr_or_wr(self):
        """Finds max. length of size.x or size.y from TR and WR"""
        max_robot_size = 0
        for x in range(0, len(self.wr_list)):
            if max_robot_size < self.wr_list[x].size.x:
                max_robot_size = self.wr_list[x].size.x
            if max_robot_size < self.wr_list[x].size.y:
                max_robot_size = self.wr_list[x].size.y

        for y in range(0, len(self.tr_list)):
            if max_robot_size < self.tr_list[y].size.x:
                max_robot_size = self.tr_list[y].size.x
            if max_robot_size < self.tr_list[y].size.y:
                max_robot_size = self.tr_list[y].size.y
        return max_robot_size

    def get_size_and_number_of_machine(self):
        """Get a list of space per machine and the quantity of the required machine_space"""
        coordinate_count = defaultdict(
            int)  # int: The default value (in this example: Coordinate) for non-existent keys is 0
        for x in range(0, len(self.machine_list)):
            coordinates = (int(self.machine_list[x].size.x), int(self.machine_list[x].size.y))
            coordinate_count[coordinates] += 1
        coordinate_list = [(Coordinates(coord[0], coord[1]), int(count)) for coord, count in coordinate_count.items()]
        return coordinate_list

    def get_every_machine_placed_in_production(self):
        machine_list_static = self.get_machine_list_static()
        machine_list_flexible = self.get_machine_list_flexible()
        if len(machine_list_static) > 0:
            self.get_static_machine_placed_in_production(machine_list_static)
        if len(machine_list_flexible) > 0:
            self.get_flexible_machine_placed_in_production(machine_list_flexible)

    def get_machine_list_static(self):
        return [machine for machine in self.machine_list if int(machine.driving_speed) == 0]

    def get_machine_list_flexible(self) -> list:
        return [machine for machine in self.machine_list if int(machine.driving_speed) != 0]

    def get_static_machine_placed_in_production(self, machine_list_static: list):
        """sets static machine in the production_layout. Alternate between one machine above sink and one below. All
        machines of one type are positioned on the same x-Axis. The next machine_type [i] is positions on the left side
        from the machine_type [i-1]"""
        number_of_machine = len(machine_list_static)
        avoiding_collision_parameter_x = 0

        space_between_machine = (
                self.get_max_length_of_tr_or_wr() * 2)  # *2 because two robots should drive between machines simultaneously
        y_start = self.sink_coordinates.y + int(
            machine_list_static[0].size.y / 2) + 1
        y_parameter = y_start
        y_upwards = y_start
        y_downwards = y_start
        collusion_parameter = machine_list_static[0].size.y

        for i in range(0, number_of_machine):
            while True:
                location_list = []
                new_coordinates = Coordinates(
                    self.sink_coordinates.x - 5 - space_between_machine - avoiding_collision_parameter_x -
                    machine_list_static[
                        i].size.x,
                    y_parameter)
                new_cell = self.get_cell(new_coordinates)

                checked_free_area_list = self.check_area_of_cells_is_free_for_entity(new_cell,
                                                                                     machine_list_static[
                                                                                         i].size, None)
                checked_free_area_list_length = len(checked_free_area_list)

                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = machine_list_static[i]
                        location_list.append(new_cell)
                    break
                else:
                    if machine_list_static[i].machine_type == machine_list_static[i - 1].machine_type or \
                            machine_list_static[
                                i].machine_type == machine_list_static[0].machine_type:
                        if machine_list_static[i].identification_number % 2 != 0:
                            y_upwards += machine_list_static[i].size.y + space_between_machine + 3
                            y_parameter = y_upwards
                        elif machine_list_static[i].identification_number % 2 == 0:
                            y_downwards -= collusion_parameter + space_between_machine + 3
                            collusion_parameter = machine_list_static[
                                i].size.y
                            y_parameter = y_downwards
                        else:
                            raise Exception(
                                'An error occurred when initialising static machines in the production_layout.')

                    else:
                        avoiding_collision_parameter_x += machine_list_static[
                                                              i].size.x + space_between_machine + 1
                        y_parameter = y_start
                        y_upwards = y_start
                        y_downwards = y_start
            self.entities_located[machine_list_static[i].identification_str] = location_list
            self.entities_init_located[machine_list_static[i].identification_str] = location_list

    def get_flexible_machine_placed_in_production(self, machine_list_flexible: list):
        """sets flexible machine in the production_layout. Alternate between one machine above source and one below. All
        machines of one type are positioned one behind the other (x-axis)"""
        number_of_machine = len(machine_list_flexible)
        avoiding_collision_parameter_x = 0

        space_between_machine = (
                self.get_max_length_of_tr_or_wr() * 2)  # *2 because two robots should drive between machines simultaneously
        y_start = self.source_coordinates.y + int(
            machine_list_flexible[0].size.y / 2) + 1
        y_parameter = y_start
        y_upwards = y_start
        y_downwards = y_start
        collusion_parameter = machine_list_flexible[0].size.y

        for i in range(0, number_of_machine):
            while True:
                location_list = []
                new_coordinates = Coordinates(
                    self.source_coordinates.x + 5 + space_between_machine + avoiding_collision_parameter_x,
                    y_parameter)
                new_cell = self.get_cell(new_coordinates)

                checked_free_area_list = self.check_area_of_cells_is_free_for_entity(new_cell,
                                                                                     machine_list_flexible[
                                                                                         i].size, None)
                checked_free_area_list_length = len(checked_free_area_list)

                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = machine_list_flexible[i]
                        location_list.append(new_cell)
                    break

                else:
                    if machine_list_flexible[i].machine_type == machine_list_flexible[i - 1].machine_type or \
                            machine_list_flexible[
                                i].machine_type == machine_list_flexible[0].machine_type:
                        avoiding_collision_parameter_x += machine_list_flexible[
                                                              i].size.x + space_between_machine + 1
                    else:

                        if machine_list_flexible[i].machine_type % 2 != 0:
                            y_upwards += machine_list_flexible[i].size.y + space_between_machine + 3
                            y_parameter = y_upwards
                            avoiding_collision_parameter_x = 0

                        elif machine_list_flexible[i].machine_type % 2 == 0:
                            y_downwards -= collusion_parameter + space_between_machine + 3
                            collusion_parameter = machine_list_flexible[
                                i].size.y
                            y_parameter = y_downwards
                            avoiding_collision_parameter_x = 0
                        else:
                            raise Exception(
                                'An error occurred when initialising flexible machines in the production_layout.')
            self.entities_located[machine_list_flexible[i].identification_str] = location_list
            self.entities_init_located[machine_list_flexible[i].identification_str] = location_list

    def get_intermediate_store_placed_in_production(self):
        """checking every machine in the production. If is space on the right side of the machine place the
        intermeidate store. Prefer the place in the center of the production."""

        placement_coordinates: Coordinates

        list_coordinates_of_neighbor_machine_of_potential_placement: list[Coordinates]
        list_coordinates_of_neighbor_machine_of_potential_placement = []

        list_intermediate_stores: list[IntermediateStore]
        list_intermediate_stores = self.service_entity.generate_intermediate_store_list()

        centered_production_coordinates = Coordinates(int((self.max_coordinate.x / 2)),
                                                      (int(self.max_coordinate.y / 2)))

        list_possible_cells: list[tuple[int, list[Cell]]]
        list_possible_cells = []

        space_between_machine = (
                self.get_max_length_of_tr_or_wr() * 2)

        for intermediate_store in list_intermediate_stores:
            for machine in self.machine_list:
                cell_list = self.entities_located.get(machine.identification_str)
                horizontal_cell = self.get_horizontal_edges_of_coordinates(cell_list)
                vertical_cell = self.get_vertical_edges_of_coordinates(cell_list)

                list_coordinates_of_neighbor_machine_of_potential_placement.append(
                    Coordinates(horizontal_cell[1], vertical_cell[1]))

            # find every machine with space on its right side (free space between machine and store for entities to drive)
            for machine_coordinates in list_coordinates_of_neighbor_machine_of_potential_placement:

                placement_coordinates = Coordinates(machine_coordinates.x + space_between_machine + 2,
                                                    machine_coordinates.y + 1)
                placement_cell = self.get_cell(placement_coordinates)
                free_size_area = intermediate_store.size

                checked_free_area_list = self.check_area_of_cells_is_free_for_entity(placement_cell, free_size_area,
                                                                                     None)

                # calculate euclidean distance for the best centred place
                if len(checked_free_area_list) != 0:
                    euc_distance = self.calculate_euclidean_distance(centered_production_coordinates,
                                                                     placement_coordinates)
                    list_possible_cells.append((euc_distance, checked_free_area_list))

            smallest_euc_distance_cell_list = self.find_shortest_distance(list_possible_cells)
            if smallest_euc_distance_cell_list is None:
                raise Exception("get_intermediate_store_placed_in_production doesnt work")
            for cell in smallest_euc_distance_cell_list:
                cell.placed_entity = intermediate_store

            self.intermediate_store_list.append(intermediate_store)
            self.entities_located[intermediate_store.identification_str] = smallest_euc_distance_cell_list
            self.entities_init_located[intermediate_store.identification_str] = smallest_euc_distance_cell_list

    def find_shortest_distance(self, possible_cells: list[tuple[int, list[Cell]]]) -> list[Cell] | None:
        """get a list[tuple] with the euc distance and return the list[Cells] with the smallest euc distance"""
        euc_distance: int
        smallest_euc_distance = 10000000

        for euc_distance, cell_list in possible_cells:
            if euc_distance < smallest_euc_distance:
                smallest_euc_distance = euc_distance
                smallest_cell_list = cell_list

        return smallest_cell_list

    def calculate_euclidean_distance(self, coord1: Coordinates, coord2: Coordinates) -> int:
        dx = coord1.x - coord2.x
        dy = coord1.y - coord2.y
        return int(math.sqrt(dx ** 2 + dy ** 2))

    def check_area_of_cells_is_free_for_entity(self, cell: Cell, free_area_size: Coordinates,
                                               free_condition_entity: Machine | WorkingRobot | TransportRobot | None) -> \
            list[Cell]:
        """get a cell and is checking if the area downwards and to the right is free; if free
        -> return list with free cells; if not free -> if not free -> return empty list"""
        list_of_checked_cells = []
        y_range_min = max(0, cell.cell_coordinates.y - free_area_size.y)
        y_range_max = cell.cell_coordinates.y
        x_range_min = cell.cell_coordinates.x
        x_range_max = cell.cell_coordinates.x + free_area_size.x

        for y in range(y_range_min, y_range_max):
            for x in range(x_range_min, x_range_max):

                if self.coordinates_in_layout(Coordinates(x, y)) is False:
                    break
                checked_cell = self.get_cell(Coordinates(x, y))

                if self.check_cell_is_free(checked_cell, free_condition_entity) is False:
                    list_of_checked_cells = []
                    return list_of_checked_cells

                else:
                    list_of_checked_cells.append(checked_cell)
        return list_of_checked_cells

    def check_area_of_cells_is_free_for_entity_movement(self, cell: Cell, free_area_size: Coordinates,
                                                        free_condition_entity: Machine | WorkingRobot | TransportRobot | None) -> \
            list[Cell]:
        """get a cell and is checking if the area downwards and to the right is free; if free
        -> return list with free cells; if not free -> if not free -> return empty list"""
        list_of_checked_cells = []
        y_range_min = max(0, cell.cell_coordinates.y - free_area_size.y)
        y_range_max = cell.cell_coordinates.y + 2
        x_range_min = cell.cell_coordinates.x
        x_range_max = cell.cell_coordinates.x + free_area_size.x

        for y in range(y_range_min, y_range_max):
            for x in range(x_range_min, x_range_max):

                if self.coordinates_in_layout(Coordinates(x, y)) is False:
                    break
                checked_cell = self.get_cell(Coordinates(x, y))

                if self.check_cell_is_free(checked_cell, free_condition_entity) is False:
                    list_of_checked_cells = []
                    return list_of_checked_cells

                else:
                    list_of_checked_cells.append(checked_cell)
        return list_of_checked_cells

    def check_cell_is_free(self, cell: Cell,
                           free_condition_entity: Machine | WorkingRobot | TransportRobot | None) -> bool:
        """Checks if the cell is empty or has an entity that is allowed to be in the cell."""
        if cell.placed_entity is None or cell.placed_entity == free_condition_entity:
            return True

        return False

    def get_cell(self, coordinates: Coordinates) -> Cell:

        return self.production_layout[len(self.production_layout) - 1 - coordinates.y][coordinates.x]

    def find_cell_in_production_layout(self, cell) -> Cell:
        for row in self.production_layout:
            for new_cell in row:
                if cell == new_cell:
                    return new_cell

    def coordinates_in_layout(self, testing_coordinates: Coordinates) -> bool:
        """Is checking if the coordinates are in the production_layout"""
        if testing_coordinates.x < 0 or testing_coordinates.x >= self.max_coordinate.x or testing_coordinates.y < 0 or \
                testing_coordinates.y >= self.max_coordinate.y:
            return False
        else:
            return True

    def get_horizontal_edges_of_coordinates(self, cell_list: list[Cell]) -> tuple[int, int]:
        right_edge_cell = 0
        left_edge_cell = self.max_coordinate.x
        for cell in cell_list:
            if cell.cell_coordinates.x > right_edge_cell:
                right_edge_cell = cell.cell_coordinates.x
            if cell.cell_coordinates.x < left_edge_cell:
                left_edge_cell = cell.cell_coordinates.x
        lowest_highest_x_coordinate = (left_edge_cell, right_edge_cell)
        return lowest_highest_x_coordinate

    def get_vertical_edges_of_coordinates(self, cell_list: list[Cell]) -> tuple[int, int]:
        upper_edge_cell = 0
        lower_edge_cell = self.max_coordinate.y

        for cell in cell_list:
            if cell.cell_coordinates.y < lower_edge_cell:
                lower_edge_cell = cell.cell_coordinates.y
            if cell.cell_coordinates.y > upper_edge_cell:
                upper_edge_cell = cell.cell_coordinates.y

        lowest_highest_y_coordinate = (lower_edge_cell, upper_edge_cell)
        return lowest_highest_y_coordinate
