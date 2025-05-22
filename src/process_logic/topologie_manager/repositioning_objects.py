from src.entity.intermediate_store import IntermediateStore
from src.entity.machine.machine import Machine
from src.production.base.coordinates import Coordinates
from src.production.production import Production


class RepositioningObjects:
    entity_assignment: list[tuple[str, str]]  # tuple[cell.identification_str, station.identification_str]
    replaced_entities: dict[str, Machine | IntermediateStore]  # str: identification_str

    def __init__(self, production: Production):
        self.production = production

        self.entity_assignment = []
        self.replaced_entities = {}

    def start_repositioning_objects_in_production(self, entity_assignment: list[tuple[str, str]]):
        self.entity_assignment = entity_assignment
        self.delete_object_from_production_layout()
        self.place_objects_in_production_layout()

    def delete_object_from_production_layout(self):
        for y in self.production.production_layout:
            for cell in y:
                placed_entity = cell.placed_entity

                if placed_entity is None:
                    continue

                if isinstance(placed_entity, (Machine, IntermediateStore)):

                    for _, station_identification_str in self.entity_assignment:
                        if placed_entity.identification_str == station_identification_str:

                            if station_identification_str not in self.replaced_entities:
                                self.replaced_entities[station_identification_str] = placed_entity

                            cell.placed_entity = None

    def place_objects_in_production_layout(self):

        for cell_identification_str, station_identification_str in self.entity_assignment:

            if station_identification_str == "Sink" or station_identification_str == "Source":
                pass
            else:
                entity = self.replaced_entities[station_identification_str]
                entity_size = entity.size

                start_cell_x_coordinate, start_cell_y_coordinate = map(int, cell_identification_str.split(":"))

                cell_list = []

                for y in range(0, entity_size.y):
                    y_coordinate = start_cell_y_coordinate - y

                    for x in range(0, entity_size.x):
                        x_coordinate = start_cell_x_coordinate + x

                        cell = self.production.get_cell(Coordinates(x_coordinate, y_coordinate))
                        cell.placed_entity = entity
                        cell_list.append(cell)

                self.production.entities_located[entity.identification_str] = cell_list