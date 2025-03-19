from src.data.coordinates import Coordinates
from src.data.production import Production
from src.data.service_starting_condition import ServiceStartingConditions
from matplotlib import pyplot as plt
import numpy as np

from src.entity_classes.transport_robot import TransportRobot
from src.entity_classes.working_robot import WorkingRobot
from src.entity_classes.machine import Machine
from src.data.constant import ColorRGB
from src.entity_classes.sink import Sink
from src.entity_classes.source import Source


class ProductionVisualisation:
    production = Production()
    service_starting_conditions = ServiceStartingConditions()

    def visualize_layout(self):
        if self.service_starting_conditions.set_visualising_via_matplotlib() is True:
            self.visualize_production_layout_in_matplotlib()
        if self.service_starting_conditions.set_visualising_via_terminal() is True:
            self.visualize_production_layout_in_terminal()

    def visualize_production_layout_in_terminal(self):
        print(self.print_layout_in_command_box())
        #print(self.print_legend())
        self.get_cell_information()

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
        #print('Cell type: ', required_cell.placed_entity)

        if required_cell.placed_entity is Source:
            print('Cell is Source')
        elif required_cell.placed_entity is Sink:
            print('Cell is Sink')
        elif required_cell.placed_entity is Machine or TransportRobot or WorkingRobot:
            print(f'{required_cell.placed_entity.identification_str}')
            print(f'{required_cell.placed_entity.processing_list}')
        elif required_cell.placed_entity is None:
            print('Cell is empty')


    def print_layout_as_a_field_in_extra_tab(self):
        """Generates a visual representation of the production layout as a 2D grid.
        The 3 Dimension is for the RGB-Colors"""
        grid_size = (
            self.production.max_coordinate.x, self.production.max_coordinate.y, 3)
        grid = np.full(grid_size, [255, 255, 255], dtype=np.uint8)
        for index, row in enumerate(self.production.production_layout):
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

    def visualize_production_layout_in_matplotlib(self):
        """Displays the production layout as a visual grid using Matplotlib"""

        grid = self.print_layout_as_a_field_in_extra_tab()
        fig, ax = plt.subplots()
        info_text = ax.text(0.95, 0.05, '', transform=ax.transAxes, fontsize=12,
                            verticalalignment='bottom', horizontalalignment='right', color='black')
        fig.canvas.mpl_connect('motion_notify_event',
                               lambda event: self.hover_for_cell_information(event, info_text))

        plt.imshow(np.flipud(grid), origin='lower')
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        plt.show()

    def hover_for_cell_information(self, event, info_text):
        """Displays information about a specific cell when hovering over it on the production layout"""
        if event.xdata is not None and event.ydata is not None:
            row = int(event.xdata)
            col = int(event.ydata)
            cell = self.production.get_cell(Coordinates(row, col))
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
