import numpy as np

from matplotlib import pyplot as plt

from src.constant.constant import ColorRGB
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot
from src.production.base.coordinates import Coordinates
from src.production.production import Production


class MatplotlibVisualisation:
    production: Production


    def __init__(self, production):
        self.production = production


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