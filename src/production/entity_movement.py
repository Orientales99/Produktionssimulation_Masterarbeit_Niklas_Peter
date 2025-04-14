from src.entity.machine.machine import Machine
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot
from src.production.base.coordinates import Coordinates
from src.production.production import Production



class EntityMovement:
    production: Production

    def __init__(self, production):
        self.production = production


    def move_entity_one_step(self, start_cell, entity: Machine | WorkingRobot | TransportRobot, path) -> bool:
        cell = start_cell

        x, y = map(int, path.split(":"))

        # up
        if Coordinates(cell.cell_coordinates.x, cell.cell_coordinates.y + 1) == Coordinates(x, y):
            if self.move_entity_upwards(entity) is True:
                return True



        # down
        if Coordinates(cell.cell_coordinates.x, cell.cell_coordinates.y - 1) == Coordinates(x, y):
            if self.move_entity_downwards(entity) is True:
                return True


        # left
        if Coordinates(cell.cell_coordinates.x - 1, cell.cell_coordinates.y) == Coordinates(x, y):
            if self.move_entity_left(entity) is True:
                return True



        # right
        if Coordinates(cell.cell_coordinates.x + 1, cell.cell_coordinates.y) == Coordinates(x, y):
            if self.move_entity_right(entity) is True:
                return True

        return False


    def check_move_possible(self, new_coordinates: Coordinates) -> bool:
        check_coordinates_in_layout = self.production.coordinates_in_layout(new_coordinates)
        if check_coordinates_in_layout is True:
            new_cell = self.production.get_cell(new_coordinates)
            if new_cell.placed_entity is not None:
                return False
            else:
                return True
        else:
            return False
        pass

    def move_entity_right(self, entity: Machine | WorkingRobot | TransportRobot) -> bool:
        """moves entity right on the production layout and checks if the move is possible (return bool)"""
        entity_cell_list = self.production.entities_located[entity.identification_str]
        lowest_highest_x_coordinate = self.production.get_horizontal_edges_of_coordinates(entity_cell_list)
        lowest_highest_y_coordinate = self.production.get_vertical_edges_of_coordinates(entity_cell_list)
        possible_move = True

        for y in range(lowest_highest_y_coordinate[0], lowest_highest_y_coordinate[1] + 1):
            possible_move = self.check_move_possible(Coordinates(lowest_highest_x_coordinate[1] + 1, y))
            if possible_move is False:
                return False

        for cell in entity_cell_list:

            # cell get the new entity attribute
            if cell.cell_coordinates.x == lowest_highest_x_coordinate[1] and cell.cell_coordinates.y == \
                    lowest_highest_y_coordinate[0]:
                for y in range(lowest_highest_y_coordinate[0], lowest_highest_y_coordinate[1] + 1):
                    new_cell = self.production.get_cell(Coordinates(lowest_highest_x_coordinate[1] + 1, y))

                    new_cell.placed_entity = entity
                    self.production.entities_located.setdefault(entity.identification_str, []).append(new_cell)

            # left side of the cell get deleted
            if cell.cell_coordinates.x == lowest_highest_x_coordinate[0]:
                for y in range(lowest_highest_y_coordinate[0], lowest_highest_y_coordinate[1] + 1):
                    new_empty_cell = self.production.get_cell(Coordinates(lowest_highest_x_coordinate[0], y))
                    new_empty_cell.placed_entity = None
                    self.production.entities_located[entity.identification_str] = [
                        cell for cell in self.production.entities_located[entity.identification_str] if
                        cell.cell_id != new_empty_cell.cell_id]
        if possible_move is True:
            return True
        else:
            return False

    def move_entity_left(self, entity: Machine | WorkingRobot | TransportRobot) -> bool:
        """moves entity left on the production layout and checks if the move is possible (return bool)"""
        entity_cell_list = self.production.entities_located[entity.identification_str]
        lowest_highest_x_coordinate = self.production.get_horizontal_edges_of_coordinates(entity_cell_list)
        lowest_highest_y_coordinate = self.production.get_vertical_edges_of_coordinates(entity_cell_list)
        possible_move = True

        for y in range(lowest_highest_y_coordinate[0], lowest_highest_y_coordinate[1] + 1):
            possible_move = self.check_move_possible(Coordinates(lowest_highest_x_coordinate[0] - 1, y))
            if possible_move is False:
                return False

        for cell in entity_cell_list:

            # cell get the new entity attribute
            if cell.cell_coordinates.x == lowest_highest_x_coordinate[0] and cell.cell_coordinates.y == \
                    lowest_highest_y_coordinate[0]:

                for y in range(lowest_highest_y_coordinate[0], lowest_highest_y_coordinate[1] + 1):
                    new_cell = self.production.get_cell(Coordinates(lowest_highest_x_coordinate[0] - 1, y))

                    if self.check_move_possible(new_cell.cell_coordinates) is False:
                        break

                    new_cell.placed_entity = entity
                    self.production.entities_located.setdefault(entity.identification_str, []).append(new_cell)

            # right side of the cell get deleted
            if cell.cell_coordinates.x == lowest_highest_x_coordinate[1] and cell.cell_coordinates.y == \
                    lowest_highest_y_coordinate[0]:
                for y in range(lowest_highest_y_coordinate[0], lowest_highest_y_coordinate[1] + 1):
                    new_empty_cell = self.production.get_cell(Coordinates(lowest_highest_x_coordinate[1], y))
                    new_empty_cell.placed_entity = None
                    self.production.entities_located[entity.identification_str] = [
                        cell for cell in self.production.entities_located[entity.identification_str] if
                        cell.cell_id != new_empty_cell.cell_id]

        if possible_move is True:
            return True
        else:
            return False

    def move_entity_upwards(self, entity: Machine | WorkingRobot | TransportRobot) -> bool:
        """moves entity upwards on the production layout and checks if the move is possible (return bool)"""
        entity_cell_list = self.production.entities_located[entity.identification_str]
        lowest_highest_x_coordinate = self.production.get_horizontal_edges_of_coordinates(entity_cell_list)
        lowest_highest_y_coordinate = self.production.get_vertical_edges_of_coordinates(entity_cell_list)
        possible_move = True

        for x in range(lowest_highest_x_coordinate[0], lowest_highest_x_coordinate[1] + 1):
            possible_move = self.check_move_possible(Coordinates(x, lowest_highest_y_coordinate[1] + 1))
            if possible_move is False:
                return False

        for cell in entity_cell_list:

            # cell get the new entity attribute
            if cell.cell_coordinates.y == lowest_highest_y_coordinate[1] and cell.cell_coordinates.x == \
                    lowest_highest_x_coordinate[0]:

                for x in range(lowest_highest_x_coordinate[0], lowest_highest_x_coordinate[1] + 1):
                    new_cell = self.production.get_cell(Coordinates(x, lowest_highest_y_coordinate[1] + 1))
                    if self.check_move_possible(new_cell.cell_coordinates) is False:
                        break
                    new_cell.placed_entity = entity
                    self.production.entities_located.setdefault(entity.identification_str, []).append(new_cell)

            # down side of the cell get deleted
            if cell.cell_coordinates.y == lowest_highest_y_coordinate[0] and cell.cell_coordinates.x == \
                    lowest_highest_x_coordinate[0]:
                for x in range(lowest_highest_x_coordinate[0], lowest_highest_x_coordinate[1] + 1):
                    new_empty_cell = self.production.get_cell(Coordinates(x, lowest_highest_y_coordinate[0]))
                    new_empty_cell.placed_entity = None
                    self.production.entities_located[entity.identification_str] = [
                        cell for cell in self.production.entities_located[entity.identification_str] if
                        cell.cell_id != new_empty_cell.cell_id]
        if possible_move is True:
            return True
        else:
            return False

    def move_entity_downwards(self, entity: Machine | WorkingRobot | TransportRobot) -> bool:
        """moves entity downwards on the production layout and checks if the move is possible (return bool)"""
        entity_cell_list = self.production.entities_located[entity.identification_str]
        lowest_highest_x_coordinate = self.production.get_horizontal_edges_of_coordinates(entity_cell_list)
        lowest_highest_y_coordinate = self.production.get_vertical_edges_of_coordinates(entity_cell_list)
        possible_move = True

        for x in range(lowest_highest_x_coordinate[0], lowest_highest_x_coordinate[1] + 1):
            possible_move = self.check_move_possible(Coordinates(x, lowest_highest_y_coordinate[0] - 1))
            if possible_move is False:
                return False

        for cell in entity_cell_list:

            # cell get the new entity attribute
            if cell.cell_coordinates.y == lowest_highest_y_coordinate[0] and cell.cell_coordinates.x == \
                    lowest_highest_x_coordinate[0]:

                for x in range(lowest_highest_x_coordinate[0], lowest_highest_x_coordinate[1] + 1):
                    new_cell = self.production.get_cell(Coordinates(x, lowest_highest_y_coordinate[0] - 1))
                    if self.check_move_possible(new_cell.cell_coordinates) is False:
                        break
                    new_cell.placed_entity = entity
                    self.production.entities_located.setdefault(entity.identification_str, []).append(new_cell)

            # upper side of the cell get deleted
            if cell.cell_coordinates.y == lowest_highest_y_coordinate[1] and cell.cell_coordinates.x == \
                    lowest_highest_x_coordinate[0]:
                for x in range(lowest_highest_x_coordinate[0], lowest_highest_x_coordinate[1] + 1):
                    new_empty_cell = self.production.get_cell(Coordinates(x, lowest_highest_y_coordinate[1]))
                    new_empty_cell.placed_entity = None
                    self.production.entities_located[entity.identification_str] = [
                        cell for cell in self.production.entities_located[entity.identification_str] if
                        cell.cell_id != new_empty_cell.cell_id]
        if possible_move is True:
            return True
        else:
            return False
