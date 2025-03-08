from dataclasses import dataclass

from src.data.production import Production
from src.data.coordinates import Coordinates


@dataclass
class PathFinding:
    production = Production()
    production_layout = production.production_layout


    def update_cell_neighbors_list(self, cell_position: Coordinates):
        """Create a list of neighbor cells which are not free """
        self.cell_neighbors_list = []
        cell = self.production.get_cell(cell_position)

        # Down
        if cell.cell_coordinates.y < len(self.production_layout) - 1 and \
                self.production.get_cell(Coordinates(cell_position.x, cell_position.y + 1)).placed_entity is not None:
            self.cell_neighbors_list.append(self.production.get_cell(Coordinates(cell_position.x, cell_position.y + 1)))

        # Up
        if cell.cell_coordinates.y > 0 and \
                self.production.get_cell(Coordinates(cell_position.x, cell_position.y - 1)).placed_entity is not None:
            self.cell_neighbors_list.append(self.production.get_cell(Coordinates(cell_position.x, cell_position.y - 1)))

        # Right
        if cell.cell_coordinates.x < len(self.production_layout[cell_position.y]) - 1 and \
                self.production.get_cell(Coordinates(cell_position.x + 1, cell_position.y)).placed_entity is not None:
            self.cell_neighbors_list.append(self.production.get_cell(Coordinates(cell_position.x + 1, cell_position.y)))

        # Left
        if cell.cell_coordinates.x > 0 and \
                self.production.get_cell(Coordinates(cell_position.x - 1, cell_position.y)).placed_entity is not None:
            self.cell_neighbors_list.append(self.production.get_cell(Coordinates(cell_position.x - 1, cell_position.y)))

        print(self.cell_neighbors_list)
