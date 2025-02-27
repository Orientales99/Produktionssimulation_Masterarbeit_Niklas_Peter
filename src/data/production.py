from src.data.cell import Cell
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

    def build_layout(self, max_coordinate: Coordinates):
        for y in reversed(range(0, max_coordinate.y)):
            row: list[Cell] = []
            for x in range(0, max_coordinate.y):
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

    def get_transport_robot_placed_in_production(self, tr_list: list):

        number_of_transport_robots = len(tr_list)
        avoiding_collision_parameter = 1

        for i in range(0, number_of_transport_robots):
            while True:
                new_coordinates_transport_robot = Coordinates(self.source_coordinates.x,
                                                              self.source_coordinates.y - tr_list[
                                                                  i].robot_size.y - avoiding_collision_parameter)
                new_cell = self.get_cell(new_coordinates_transport_robot)
                checked_free_area_list = self.check_area_of_cells_is_free(new_cell, tr_list[i].robot_size)
                checked_free_area_list_length = len(checked_free_area_list)
                if checked_free_area_list_length != 0:
                    for x in range(0, checked_free_area_list_length):
                        new_cell = checked_free_area_list[x]
                        new_cell.placed_entity = tr_list[i]
                    break
                else:
                    avoiding_collision_parameter -= tr_list[i].robot_size.y - 1

    def check_area_of_cells_is_free(self, cell: Cell, free_area_size: Coordinates) -> list:
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

    def check_cell_is_free(self, cell: Cell):
        if cell.placed_entity is None:
            return True
        else:
            return False

    def get_cell(self, coordinates: Coordinates) -> Cell:
        return self.production_layout[len(self.production_layout) - 1 - coordinates.y][coordinates.x]

    def print_layout(self, max_coordinate: Coordinates):
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
                    print_layout_str += ' \U0001F7E3 '
                elif type(cell.placed_entity) is WorkingRobot:
                    print_layout_str += ' \U0001F535 '
                elif type(cell.placed_entity) is Source or Sink:
                    print_layout_str += ' \U0001F534 '
                else:
                    print_layout_str += ' Error '

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
        print('\u26AA ist ein leeres unbenutzes Feld')
        print('\n \U0001F534 ist eine Maschine ')
        print('\n \U0001F7E3 ist ein Transport Robot')
        print('\n \U0001F535 ist ein Working Robot')
        print('\n \U0001F534 ist die Source (links) und Sink (rechts)')

    def get_transport_robot_placed_in_production(self):
        pass

    def get_machine_placed_in_production(self):
        pass

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
