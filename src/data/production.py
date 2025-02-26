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

    def build_layout(self, max_x_coordinate: int, max_y_coordinate: int):
        for y in reversed(range(0, max_y_coordinate)):
            row: list[Cell] = []
            for x in range(0, max_x_coordinate):
                cell = Cell(x, y, None)
                row.append(cell)
            self.production_layout.append(row)

    def set_source_in_production_layout(self, max_x_coordinate: int, max_y_coordinate: int):
        y_coordinate_source = int(max_y_coordinate / 2)

        for y_index, row in enumerate(self.production_layout):
            if y_index == y_coordinate_source:
                cell = row[0]
                cell.placed_entity = Source(0, 0, 0)
                self.source_coordinates = Coordinates(0, y_index)
                return cell

    def set_sink_in_production_layout(self, max_x_coordinate: int, max_y_coordinate: int):
        coordinates = Coordinates(int(max_x_coordinate - 1), int(max_y_coordinate/2))
        cell = self.get_cell(coordinates)
        cell.placed_entity = Sink(0, 0, 0)

    def get_cell(self, coordinates: Coordinates):

        cell = self.production_layout[len(self.production_layout) - coordinates.y][coordinates.x]

        return cell

    def print_layout(self, max_x_coordinate: int, max_y_coordinate: int):
        print_layout_str = ''

        for index, row in enumerate(self.production_layout):

            first_cell_in_row = row[0].y_coordinate

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
        for x in range(0, max_x_coordinate):
            if x < 10 and x % 5 == 0:
                print_layout_str += f'  {x} '
            elif x >= 10 and x % 5 == 0:
                print_layout_str += f' {x} '
            else:
                print_layout_str += (' \u26AB ')
        return print_layout_str

    def print_legend(self):
        print('\u26AA ist ein leeres unbenutzes Feld')
        print('\n \U0001F534 ist eine Maschine ')
        print('\n \U0001F7E3 ist ein Transport Robot')
        print('\n \U0001F535 ist ein Working Robot')
        print('\n \U0001F534 ist die Source (links) und Sink (rechts)')

    def get_working_robot_placed_in_production(self, wr_list):
        new_x_coordinate_working_robot = 0
        new_y_coordinate_working_robot = 0

        number_of_working_robots = len(wr_list)
        avoiding_collision_parameter = 1
        for x in range(0, number_of_working_robots):

            for y_coordinate, x_coordinate in enumerate(self.production_layout):
                for cell in x_coordinate:
                    if cell.placed_entity == Source:
                        new_y_coordinate_working_robot = cell.y_coordinate - int(
                            wr_list[x].robot_size[1])
                        new_x_coordinate_working_robot = cell.x_coordinate
                        print('x:', new_x_coordinate_working_robot, 'y:', new_y_coordinate_working_robot)

            for y_coordinate, x_coordinate in enumerate(self.production_layout):
                for cell in x_coordinate:
                    if y_coordinate == new_y_coordinate_working_robot and x_coordinate == new_x_coordinate_working_robot:
                        cell.placed_entity = WorkingRobot

    def get_transport_robot_placed_in_production(self):
        pass

    def get_machine_placed_in_production(self):
        pass
