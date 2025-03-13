from dataclasses import dataclass
from queue import PriorityQueue

from src.data.production import Production
from src.data.coordinates import Coordinates
from src.data.cell import Cell


@dataclass
class PathFinding:
    production = Production()
    production_layout = production.production_layout
    path_line_list = []

    def run_a_star_algorithm(self, start_cell: Cell, end_cell: Cell) -> bool:
        count = 0
        open_set = PriorityQueue()
        open_set.put((0, count, start_cell))  # item (0) = f_score, count = keep track, when it put into Queue
        came_from = {}
        g_score = {cell.cell_id: float("inf") for row in self.production_layout for cell in row}
        g_score[start_cell.cell_id] = 0
        f_score = {cell.cell_id: float("inf") for row in self.production_layout for cell in row}
        f_score[start_cell.cell_id] = self.calculate_h_score(start_cell.cell_coordinates, end_cell.cell_coordinates)

        open_set_hash = {start_cell.cell_id}  # creating a hash to check if cell is in PriorityQueue

        while not open_set.empty():

            current_cell = open_set.get()[2]
            open_set_hash.remove(current_cell.cell_id)

            if current_cell.cell_coordinates == end_cell.cell_coordinates:
                self.reconstruct_path(came_from, end_cell.cell_id)
                return True

            current_cell.neighbors_list = self.get_current_cell_neighbors(current_cell.cell_coordinates)
            for neighbor in current_cell.neighbors_list:
                temp_g_score = g_score[current_cell.cell_id] + 1

                if temp_g_score < g_score[neighbor.cell_id]:
                    came_from[neighbor.cell_id] = current_cell.cell_id
                    g_score[neighbor.cell_id] = temp_g_score
                    f_score[neighbor.cell_id] = temp_g_score + self.calculate_h_score(neighbor.cell_coordinates,
                                                                                      end_cell.cell_coordinates)

                    if neighbor.cell_id not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor.cell_id], count, neighbor))
                        open_set_hash.add(neighbor.cell_id)
        return False

    def reconstruct_path(self, came_from, current_cell_id):
        path = []

        while current_cell_id in came_from:  # Gehe rückwärts durch den Pfad
            path.append(current_cell_id)
            current_cell_id = came_from[current_cell_id]  # Nächste Zelle auf dem Pfad

        path.reverse()  # Umkehren, damit der Pfad von Start → Ziel geht
        self.path_line_list = path  # Speichern des rekonstruierten Pfads

        print("Rekonstruierter Pfad:", self.path_line_list)

    def calculate_h_score(self, start_coordinates: Coordinates, end_coordinates: Coordinates):
        return abs(start_coordinates.x - end_coordinates.x) + abs(start_coordinates.y - end_coordinates.y)

    def get_current_cell_neighbors(self, cell_position: Coordinates) -> list[Cell]:
        """Create a list of neighbor cells which are free """
        cell_neighbors_list = []
        cell = self.production.get_cell(cell_position)

        # Down
        if cell.cell_coordinates.y < len(self.production_layout) - 1 and \
                self.production.get_cell(Coordinates(cell_position.x, cell_position.y + 1)).placed_entity is None:
            cell_neighbors_list.append(self.production.get_cell(Coordinates(cell_position.x, cell_position.y + 1)))

        # Up
        if cell.cell_coordinates.y > 0 and \
                self.production.get_cell(Coordinates(cell_position.x, cell_position.y - 1)).placed_entity is None:
            cell_neighbors_list.append(self.production.get_cell(Coordinates(cell_position.x, cell_position.y - 1)))

        # Right
        if cell.cell_coordinates.x < len(self.production_layout[cell_position.y]) - 1 and \
                self.production.get_cell(Coordinates(cell_position.x + 1, cell_position.y)).placed_entity is None:
            cell_neighbors_list.append(self.production.get_cell(Coordinates(cell_position.x + 1, cell_position.y)))

        # Left
        if cell.cell_coordinates.x > 0 and \
                self.production.get_cell(Coordinates(cell_position.x - 1, cell_position.y)).placed_entity is None:
            cell_neighbors_list.append(self.production.get_cell(Coordinates(cell_position.x - 1, cell_position.y)))

        return cell_neighbors_list

    def move_entity_along_path(self):
        pass
