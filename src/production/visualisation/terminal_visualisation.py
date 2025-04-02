from src.entity.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_robot import TransportRobot
from src.entity.working_robot import WorkingRobot
from src.production.base.coordinates import Coordinates
from src.production.production import Production


class TerminalVisualisation:
    production: Production

    def __init__(self, production):
        self.production = production

    def visualize_production_layout_in_terminal(self):
        print(self.print_layout_in_command_box())
        # print(self.print_legend())
        # self.get_cell_information()

    def print_layout_in_command_box(self) -> str:
        """Build a string and every cell in the list production_layouts gets a UTF-8 code Symbol"""
        print_layout_str = ''

        for index, row in enumerate(self.production.production_layout):

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
                        'A cell has an invalid cell.playced_entity, which was not taken into account '
                        'in the conditions of def print_layout.')

            print_layout_str += "\n"
        print_layout_str += '      '
        for x in range(0, self.production.max_coordinate.x):
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

    def get_cell_information(self):
        print('From which cell do you require information:')
        more_information = 'y'

        while more_information == 'y':
            x_coordinate = int(input('X:'))
            y_coordinate = int(input('Y: '))
            required_coordinate = Coordinates(x_coordinate, y_coordinate)
            self.print_cell_information((required_coordinate))
            more_information = input('Do you need more information? (y/n): ')
        pass

    def print_cell_information(self, coordinates: Coordinates):
        required_cell = self.production.get_cell(coordinates)
        print('x: ', required_cell.cell_coordinates.x)
        print('y: ', required_cell.cell_coordinates.y)
        # print('Cell type: ', required_cell.placed_entity)

        if required_cell.placed_entity is Source:
            print('Cell is Source')
        elif required_cell.placed_entity is Sink:
            print('Cell is Sink')
        elif required_cell.placed_entity is Machine or TransportRobot or WorkingRobot:
            print(f'{required_cell.placed_entity.identification_str}')
            print(f'{required_cell.placed_entity.processing_list}')
            print(f'{required_cell.placed_entity.processing_list_queue_length}')
        elif required_cell.placed_entity is None:
            print('Cell is empty')