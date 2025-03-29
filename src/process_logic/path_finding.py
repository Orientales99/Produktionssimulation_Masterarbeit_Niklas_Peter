from dataclasses import dataclass
from queue import PriorityQueue

from src.production.entity_movement import EntityMovement
from src.production.production import Production
from src.production.base.coordinates import Coordinates
from src.production.base.cell import Cell
from src.entity.machine import Machine
from src.entity.transport_robot import TransportRobot
from src.entity.working_robot import WorkingRobot
from src.production.production_visualisation import ProductionVisualisation


class PathFinding:
    production: Production
    path_line_list = []

    def __init__(self, production: Production):
        self.production = production
        self.entity_movement = EntityMovement(self.production)
        self.path_line_list = []

    def get_path_for_entity(self, entity: Machine | WorkingRobot | TransportRobot, end_coordinate: Coordinates):
        start_coordinate = self.get_start_coordinates_from_entity(entity)
        # print(f" Start: {start_coordinate}, End: {end_coordinate}")
        start_cell = self.get_start_cell_from_entity(entity)
        end_cell = self.production.get_cell(end_coordinate)
        if self.run_a_star_algorithm(start_cell, end_cell, entity) is False:
            return Exception(
                f"Path finding doesn't work. Entity: {entity}, Start: {start_coordinate}, End: {end_coordinate}")

        return self.path_line_list

    def run_a_star_algorithm(self, start_cell: Cell, end_cell: Cell,
                             moving_entity: Machine | WorkingRobot | TransportRobot) -> bool:

        count = 0
        open_set = PriorityQueue()
        open_set.put((0, count, start_cell))  # item (0) = f_score, count = keep track, when it put into Queue
        came_from = {}
        g_score = {cell.cell_id: float("inf") for row in self.production.production_layout for cell in row}
        g_score[start_cell.cell_id] = 0
        f_score = {cell.cell_id: float("inf") for row in self.production.production_layout for cell in row}
        f_score[start_cell.cell_id] = self.calculate_h_score(start_cell.cell_coordinates, end_cell.cell_coordinates)

        open_set_hash = {start_cell.cell_id}  # creating a hash to check if cell is in PriorityQueue

        while not open_set.empty():

            current_cell = open_set.get()[2]
            open_set_hash.remove(current_cell.cell_id)

            if current_cell.cell_coordinates == end_cell.cell_coordinates:
                self.reconstruct_path(came_from, end_cell.cell_id)
                return True

            current_cell.neighbors_list = self.check_neighbor_cells_complete_wide(current_cell.cell_coordinates,
                                                                                  moving_entity)
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
        self.path_line_list = path

    def calculate_h_score(self, start_coordinates: Coordinates, end_coordinates: Coordinates):
        return abs(start_coordinates.x - end_coordinates.x) + abs(start_coordinates.y - end_coordinates.y)

    def get_current_cell_neighbors(self, cell_position: Coordinates, current_cell: Cell, moving_entity) -> list[Cell]:
        """Checks if the neighbors of current cell are empty or part of the moving_entity. In will the cell be added to
        the cell_neighbors_list. Cell_position are the coordinates of current_cell"""
        cell_neighbors_down = self.get_current_cell_neighbor_down(cell_position, current_cell, moving_entity)
        cell_neighbors_up = self.get_current_cell_neighbor_up(cell_position, current_cell, moving_entity)
        cell_neighbors_right = self.get_current_cell_neighbor_right(cell_position, current_cell, moving_entity)
        cell_neighbors_left = self.get_current_cell_neighbor_left(cell_position, current_cell, moving_entity)

        cell_neighbors_list = [cell for cell in
                               [cell_neighbors_down, cell_neighbors_up, cell_neighbors_right, cell_neighbors_left] if
                               cell is not None]
        return cell_neighbors_list

    def get_current_cell_neighbor_up(self, cell_position: Coordinates, current_cell: Cell, moving_entity) -> Cell:
        if current_cell.cell_coordinates.y < len(self.production.production_layout) - 1 and \
                (self.production.get_cell(Coordinates(cell_position.x,
                                                      cell_position.y + 1)).placed_entity is None or self.production.get_cell(
                    Coordinates(cell_position.x, cell_position.y + 1)).placed_entity is moving_entity):
            return self.production.get_cell(Coordinates(cell_position.x, cell_position.y + 1))

    def get_current_cell_neighbor_down(self, cell_position: Coordinates, current_cell: Cell, moving_entity) -> Cell:
        if current_cell.cell_coordinates.y > 0 and \
                (self.production.get_cell(Coordinates(cell_position.x,
                                                      cell_position.y - 1)).placed_entity is None or self.production.get_cell(
                    Coordinates(cell_position.x, cell_position.y - 1)).placed_entity is moving_entity):
            return self.production.get_cell(Coordinates(cell_position.x, cell_position.y - 1))

    def get_current_cell_neighbor_right(self, cell_position: Coordinates, current_cell: Cell, moving_entity) -> Cell:
        if current_cell.cell_coordinates.x < len(self.production.production_layout[cell_position.y]) - 1 and \
                (self.production.get_cell(Coordinates(cell_position.x + 1,
                                                      cell_position.y)).placed_entity is None or self.production.get_cell(
                    Coordinates(cell_position.x + 1, cell_position.y)).placed_entity is moving_entity):
            return self.production.get_cell(Coordinates(cell_position.x + 1, cell_position.y))

    def get_current_cell_neighbor_left(self, cell_position: Coordinates, current_cell: Cell, moving_entity) -> Cell:
        if current_cell.cell_coordinates.x > 0 and \
                (self.production.get_cell(Coordinates(cell_position.x - 1,
                                                      cell_position.y)).placed_entity is None or self.production.get_cell(
                    Coordinates(cell_position.x - 1, cell_position.y)).placed_entity is moving_entity):
            return self.production.get_cell(Coordinates(cell_position.x - 1, cell_position.y))

    def check_neighbor_cells_complete_wide(self, cell_position: Coordinates,
                                           entity: Machine | WorkingRobot | TransportRobot) -> list[Cell]:
        current_cell = self.production.get_cell(cell_position)
        cell_neighbors_list = self.get_current_cell_neighbors(cell_position, current_cell, entity)
        cell_neighbors_list_copy = cell_neighbors_list

        for cell in cell_neighbors_list_copy:
            entity_cell_list = self.production.check_area_of_cells_is_free_for_entity_movement(cell, Coordinates(
                entity.size.x + 1, entity.size.y + 1), entity)
            if len(entity_cell_list) == 0:
                cell_neighbors_list.remove(cell)

        return cell_neighbors_list

    def get_start_cell_from_entity(self, entity: Machine | WorkingRobot | TransportRobot) -> Coordinates:
        """Starting point is the upper right corner of the entity"""
        start_coordinates = self.get_start_coordinates_from_entity(entity)
        start_cell = self.production.get_cell(start_coordinates)
        return start_cell

    def get_start_coordinates_from_entity(self, entity: Machine | WorkingRobot | TransportRobot) -> Coordinates:
        """Starting point is the upper right corner of the entity"""
        cell_list = self.production.entities_located.get(entity.identification_str, [])
        horizontal_edges = self.production.get_horizontal_edges_of_coordinates(cell_list)
        vertical_edges = self.production.get_vertical_edges_of_coordinates(cell_list)

        return Coordinates(horizontal_edges[0], vertical_edges[1])
