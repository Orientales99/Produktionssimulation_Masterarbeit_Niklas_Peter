from src.data.cell import Cell
from src.data.machine import Machine
from src.data.order_service import OrderService
from src.data.sink import Sink
from src.data.source import Source
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


class Production:
    production_layout: list[list[Cell]] = []
    order_service = OrderService()

    def build_layout(self, max_x_coordinate: int, max_y_coordinate: int):
        for y in reversed(range(1, max_y_coordinate)):
            row: list[Cell] = []
            for x in range(1, max_x_coordinate):
                cell = Cell(x, y, None)
                row.append(cell)
            self.production_layout.append(row)

    def print_layout(self, max_x_coordinate: int, max_y_coordinate: int):
        print_layout_str = ''

        for y_coordinate, x_coordinate in enumerate(self.production_layout):
            # index_variable_y = (max_y_coordinate - 1) - y_coordinate
            index_variable_y = y_coordinate

            if index_variable_y < 10:
                print_layout_str += f'   {index_variable_y}  '
            else:
                print_layout_str += f'  {index_variable_y}  '
            for cell in x_coordinate:

                if cell.placed_entity is None:
                    print_layout_str += ' \u26AA '
                elif type(cell.placed_entity) == Machine:
                    print_layout_str += ' \U0001F534 '
                elif type(cell.placed_entity) == TransportRobot:
                    print_layout_str += ' \U0001F7E3 '
                elif type(cell.placed_entity) == WorkingRobot:
                    print_layout_str += ' \U0001F535 '
                elif type(cell.placed_entity) == Source or Sink:
                    print_layout_str += ' \U0001F534 '
                else:
                    print_layout_str += ' Error '

            print_layout_str += "\n"
        print_layout_str += '      '
        for x in range(1, max_x_coordinate):
            if x < 10 and x % 5 == 0 or x == 1:
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

    def get_source_in_production_layout(self, max_x_coordinate: int, max_y_coordinate: int):
        y_coordinate_source = int(max_y_coordinate / 2)

        for y_index, row in enumerate(self.production_layout):
            if y_index == y_coordinate_source:
                cell = row[0]
                cell.placed_entity = Source
                return cell

    def get_sink_in_production_layout(self, max_x_coordinate: int, max_y_coordinate: int):
        y_coordinate_sink = int(max_y_coordinate / 2)
        x_coordinate_sink = int(max_x_coordinate - 2)
        for y_index, row in enumerate(self.production_layout):
            if y_index == y_coordinate_sink:
                cell = row[x_coordinate_sink]
                cell.placed_entity = Sink
                return cell

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
