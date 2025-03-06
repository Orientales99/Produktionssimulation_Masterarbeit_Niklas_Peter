from collections import defaultdict

import numpy as np
from matplotlib import pyplot as plt

from src.data.cell import Cell
from src.data.constant import ColorRGB
from src.data.coordinates import Coordinates
from src.data.machine import Machine
from src.data.order_service import OrderService
from src.data.sink import Sink
from src.data.source import Source
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


class Production:
    production_layout: list[list[Cell]] = []
    order_service = OrderService()
    source_coordinates: Coordinates
    sink_coordinates: Coordinates
    wr_list = []
    self.tr_list = []
    machine_list = []
    max_coordinate = None

    def create_production(self):
        self.build_layout(self.max_coordinate)
        self.set_source_in_production_layout(self.max_coordinate)
        self.set_sink_in_production_layout(self.max_coordinate)

    def set_entities(self):

        self.get_working_robot_placed_in_production()
        self.get_transport_robot_placed_in_production()
        self.get_every_machine_placed_in_production()

    def get_data_from_order_service(self):
        self.wr_list = self.order_service.generate_wr_list()
        self.tr_list = self.order_service.generate_tr_list()
        self.machine_list = self.order_service.generate_machine_list()
        pass

    def build_layout(self, max_coordinate: Coordinates):
        """Forms a list in a list (production_layout), which represents a coordinate system consisting of the class
        Cell"""
        for y in reversed(range(0, max_coordinate.y)):
            row: list[Cell] = []
            for x in range(0, max_coordinate.x):
                cell = Cell(Coordinates(x, y), None)
                row.append(cell)
            self.production_layout.append(row)

    def set_source_in_production_layout(self, max_coordinate: Coordinates):
        self.source_coordinates = Coordinates(0, int(max_coordinate.y / 2))
        cell = self.get_cell(self.source_coordinates)
        cell.placed_entity = Source(0, 0, 0)

    def set_sink_in_production_layout(self, max_coordinate: Coordinates):
        self.sink_coordinates = Coordinates(int(max_coordinate.x - 1), int(max_coordinate.y / 2))
        cell = self.get_cell(self.sink_coordinates)
        cell.placed_entity = Sink(0, 0, 0)

    def get_working_robot_placed_in_production(self, wr_list: list):
        number_of_working_robots = len(wr_list)
        avoiding_collision_parameter = 1
        for i in range(0, number_of_working_robots):
            while True:
                new_coordinates_working_robot = Coordinates(self.source_coordinates.x,
                                                            self.source_coordinates.y + wr_list[
                                                                i].robot_size.y + 1 + avoiding_collision_parameter)
                new_cell = self.get_cell(new_coordinates_working_robot)
                checked_free_area_list = self.check_area_of_cells_is_free(new_cell, wr_list[i].robot_size)
                checked_free_area_list_length = len(checked_free_area_list)
                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = wr_list[i]
                    break
                else:
                    avoiding_collision_parameter += wr_list[i].robot_size.y + 1

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
        for x in range(0, len(wr_list)):
            if max_robot_size < wr_list[x].robot_size.x:
                max_robot_size = wr_list[x].robot_size.x
            if max_robot_size < wr_list[x].robot_size.y:
                max_robot_size = wr_list[x].robot_size.y

        for y in range(0, len(self.tr_list)):
            if max_robot_size < self.tr_list[y].robot_size.x:
                max_robot_size = self.tr_list[y].robot_size.x
            if max_robot_size < self.tr_list[y].robot_size.y:
                max_robot_size = self.tr_list[y].robot_size.y
        return max_robot_size

    def safe_space_for_placing_machines_in_production(self, machine_list) -> list:
        safed_cells_for_machine_list = []
        pass

    def get_size_and_number_of_machine(self, machine_list):
        """Get a list of space per machine and the quantity of the required machine_space"""
        coordinate_count = defaultdict(
            int)  # int: The default value (in this example: Coordinate) for non-existent keys is 0
        for x in range(0, len(machine_list)):
            coordinates = (int(machine_list[x].machine_size.x), int(machine_list[x].machine_size.y))
            coordinate_count[coordinates] += 1
        coordinate_list = [(Coordinates(coord[0], coord[1]), int(count)) for coord, count in coordinate_count.items()]
        return coordinate_list

    def get_every_machine_placed_in_production(self):
        machine_list_static = self.get_machine_list_static(machine_list)
        machine_list_flexible = self.get_machine_list_flexible(machine_list)
        self.get_static_machine_placed_in_production(machine_list_static)
        self.get_flexible_machine_placed_in_production(machine_list_flexible)

    def get_machine_list_static(self, machine_list):
        return [machine for machine in machine_list if int(machine.driving_speed) == 0]

    def get_machine_list_flexible(self, machine_list) -> list:
        return [machine for machine in machine_list if int(machine.driving_speed) != 0]

    def get_static_machine_placed_in_production(self):
        machine_list = machine_list_static
        number_of_machine = len(machine_list)
        avoiding_collision_parameter_x = 0

        space_between_machine = (self.get_max_length_of_tr_or_wr() * 2)  # *2 because two robots should drive between machines simultaneously
        y_start = self.sink_coordinates.y + int(
            (machine_list[0].machine_size.y) / 2) + 1
        y_parameter = y_start
        y_upwards = y_start
        y_downwards = y_start
        collusion_parameter = machine_list[0].machine_size.y

        for i in range(0, number_of_machine):
            while True:
                new_coordinates = Coordinates(
                    self.sink_coordinates.x - 5 - space_between_machine - avoiding_collision_parameter_x - machine_list[
                        i].machine_size.x,
                    y_parameter)
                new_cell = self.get_cell(new_coordinates)

                checked_free_area_list = self.check_area_of_cells_is_free(new_cell, machine_list[i].machine_size)
                checked_free_area_list_length = len(checked_free_area_list)

                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = machine_list[i]
                    break
                else:
                    if machine_list[i].machine_type == machine_list[i - 1].machine_type or machine_list[
                        i].machine_type == machine_list[0].machine_type:
                        if machine_list[i].identification_number % 2 != 0:
                            y_upwards += machine_list[i].machine_size.y + space_between_machine + 3
                            y_parameter = y_upwards
                        elif machine_list[i].identification_number % 2 == 0:
                            y_downwards -= collusion_parameter + space_between_machine + 3
                            collusion_parameter = machine_list[
                                i].machine_size.y
                            y_parameter = y_downwards
                        else:
                            raise Exception(
                                'An error occurred when initialising static machines in the production_layout.')

                    else:
                        avoiding_collision_parameter_x += machine_list[i].machine_size.x + space_between_machine + 1
                        y_parameter = y_start
                        y_upwards = y_start
                        y_downwards = y_start

    def get_flexible_machine_placed_in_production(self):
        """sets flexible machine in the production_layout. Alternate between one machine above source and one below. All
        machines of one type are positioned one behind the other (x-axis)"""
        machine_list = machine_list_flexible
        number_of_machine = len(machine_list)
        avoiding_collision_parameter_x = 0

        space_between_machine = (self.get_max_length_of_tr_or_wr() * 2)  # *2 because two robots should drive between machines simultaneously
        y_start = self.source_coordinates.y + int(
            (machine_list[0].machine_size.y) / 2) + 1
        y_parameter = y_start
        y_upwards = y_start
        y_downwards = y_start
        collusion_parameter = machine_list[0].machine_size.y

        for i in range(0, number_of_machine):
            while True:
                new_coordinates = Coordinates(
                    self.source_coordinates.x + 5 + space_between_machine + avoiding_collision_parameter_x,
                    y_parameter)
                new_cell = self.get_cell(new_coordinates)

                checked_free_area_list = self.check_area_of_cells_is_free(new_cell, machine_list[i].machine_size)
                checked_free_area_list_length = len(checked_free_area_list)

                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = machine_list[i]
                    break
                else:
                    if machine_list[i].machine_type == machine_list[i - 1].machine_type or machine_list[
                        i].machine_type == machine_list[0].machine_type:
                        avoiding_collision_parameter_x += machine_list[i].machine_size.x + space_between_machine + 1
                    else:
                        if machine_list[i].machine_type % 2 != 0:
                            y_upwards += machine_list[i].machine_size.y + space_between_machine + 3
                            y_parameter = y_upwards
                            avoiding_collision_parameter_x = 0
                        elif machine_list[i].machine_type % 2 == 0:
                            y_downwards -= collusion_parameter + space_between_machine + 3
                            collusion_parameter = machine_list[
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

    def print_layout_in_command_box(self, max_coordinate: Coordinates) -> str:
        """Build a string and every cell in the list production_layouts gets a UTF-8 code Symbol"""
        print_layout_str = ''

        for index, row in enumerate(self.production_layout):

            first_cell_in_row = row[0].cell_coordinates.y

            if first_cell_in_row < 10:
                print_layout_str += f'   {first_cell_in_row}  '
            else:
                print_layout_str += f'  {first_cell_in_row}  '
            for cell in row:

                if cell.placed_entity is None:
                    print_layout_str += ' \u26AA '
                elif type(cell.placed_entity) is Machine:
                    print_layout_str += ' \U0001F534 '
                elif type(cell.placed_entity) is TransportRobot:
                    print_layout_str += ' \u26AB '
                elif type(cell.placed_entity) is WorkingRobot:
                    print_layout_str += ' \U0001F535 '
                elif type(cell.placed_entity) is Source or Sink:
                    print_layout_str += ' \U0001F534 '
                else:
                    raise Exception(
                        'A cell has an invalid cell.playced_entity, which was not taken into account in the conditions of def print_layout.')

            print_layout_str += "\n"
        print_layout_str += '      '
        for x in range(0, max_coordinate.x):
            if x < 10 and x % 5 == 0:
                print_layout_str += f'  {x} '
            elif x >= 10 and x % 5 == 0:
                print_layout_str += f' {x} '
            else:
                print_layout_str += ' \u26AB '
        return print_layout_str

    def print_legend(self):
        """Legend of the production_layout will be printed"""
        print('\u26AA ist ein leeres unbenutzes Feld')
        print('\n \U0001F534 ist eine Maschine ')
        print('\n \u26AB ist ein Transport Robot')
        print('\n \U0001F535 ist ein Working Robot')
        print('\n \U0001F534 ist die Source (links) und Sink (rechts)')

    def print_cell_information(self, coordinates: Coordinates):
        required_cell = self.get_cell(coordinates)
        print('x: ', required_cell.cell_coordinates.x)
        print('y: ', required_cell.cell_coordinates.y)
        print('Cell type: ', required_cell.placed_entity)

        if required_cell.placed_entity is Machine or TransportRobot or WorkingRobot:
            print('Machine ID: ', required_cell.placed_entity.identification_number)
        elif required_cell.placed_entity is TransportRobot:
            print('TR ID: ', required_cell.placed_entity.identification_number)
        elif required_cell.placed_entity is WorkingRobot:
            print('WR ID: ', required_cell.placed_entity.identification_number)
        elif required_cell.placed_entity is Source:
            print('Cell is Source')
        elif required_cell.placed_entity is Sink:
            print('Cell is Sink')
        elif required_cell.placed_entity is None:
            print('Cell is empty')

    def print_layout_as_a_field_in_extra_tab(self, max_coordinate: Coordinates):
        grid_size = (max_coordinate.x, max_coordinate.y, 3)  # 3 Dimensions for RGB-Colors
        grid = np.full(grid_size, [255, 255, 255], dtype=np.uint8)
        for index, row in enumerate(self.production_layout):
            for cell in row:
                if cell.placed_entity is None:
                    grid[index, cell.cell_coordinates.x] = ColorRGB.WHITE.value
                elif type(cell.placed_entity) is Machine:
                    grid[index, cell.cell_coordinates.x] = ColorRGB.BLACK.value
                elif type(cell.placed_entity) is TransportRobot:
                    grid[index, cell.cell_coordinates.x] = ColorRGB.BROWN.value
                elif type(cell.placed_entity) is WorkingRobot:
                    grid[index, cell.cell_coordinates.x] = ColorRGB.ORANGE.value
                elif type(cell.placed_entity) is Source or Sink:
                    grid[index, cell.cell_coordinates.x] = ColorRGB.RED.value
        return grid

    def hover_for_cell_information(self, event, info_text):
        if event.xdata is not None and event.ydata is not None:
            row = int(event.xdata)
            col = int(event.ydata)
            cell = self.get_cell(Coordinates(row, col))
            # Hier können beliebige weitere Informationen zu den Zellen angezeigt werden
            if cell.placed_entity is None:
                cell_info = f"Row: {row}, Col: {col}, None"
                info_text.set_text(cell_info)
            elif type(cell.placed_entity) is Machine:
                cell_info = f"Row: {row}, Col: {col}, MA{cell.placed_entity.machine_type}, ID: {cell.placed_entity.identification_number}"
                info_text.set_text(cell_info)
            elif type(cell.placed_entity) is TransportRobot:
                cell_info = f"Row: {row}, Col: {col}, TR(ID:{cell.placed_entity.identification_number})"
                info_text.set_text(cell_info)
            elif type(cell.placed_entity) is WorkingRobot:
                cell_info = f"Row: {row}, Col: {col}, WR(ID:{cell.placed_entity.identification_number})"
                info_text.set_text(cell_info)
            elif type(cell.placed_entity) is Source:
                cell_info = f"Row: {row}, Col: {col}, Source"
                info_text.set_text(cell_info)
            elif type(cell.placed_entity) is Sink:
                cell_info = f"Row: {row}, Col: {col}, Sink"
                info_text.set_text(cell_info)
        plt.draw()

    def coordinates_in_layout(self, max_coordinates: Coordinates, testing_coordinates: Coordinates) -> bool:
        """Is checking if the coordinates are in the production_layout"""
        if testing_coordinates.x >= 0 or testing_coordinates.x < max_coordinates.x or testing_coordinates.y >= 0 or testing_coordinates.y < max_coordinates.y:
            return True
        else:
            return False
