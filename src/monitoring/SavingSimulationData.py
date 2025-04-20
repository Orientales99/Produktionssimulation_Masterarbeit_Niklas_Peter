import json
import os
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.production.production import Production


class SavingSimulationData:
    production: Production
    entities_located: {str, list[Cell]} # {entity.identification_str, list[Cell]}
    list_every_entity_identification_str: list[str]
    saving_entity_data_list: list[Cell]

    def __init__(self, environment, production):
        self.env = environment
        self.production = production
        self.entities_located = self.production.entities_located[:]
        self.list_every_entity_identification_str= list[str]
        self.saving_entity_data_list = []

    def save_every_entity_identification_str(self):
        self.list_every_entity_identification_str = list(self.entities_located.keys())

    def start_saving_simulation_data(self):
        self.save_new_entity_dictionary()
        self.save_one_cell_of_each_entity()

    def save_new_entity_dictionary(self):
        self.entities_located = self.production.entities_located[:]

    def save_one_cell_of_each_entity(self):
        """Looping through every entity and its individual cell_list.
            Saving the cell in the top left corner of each entity."""
        self.saving_entity_data_list = []
        for identification_str in self.list_every_entity_identification_str:
            cell_list = self.entities_located.get(identification_str, [])
            horizontal_edges = self.production.get_horizontal_edges_of_coordinates(cell_list)
            vertical_edges = self.production.get_vertical_edges_of_coordinates(cell_list)

            cell = self.production.get_cell(Coordinates(horizontal_edges[0], vertical_edges[1]))
            self.saving_entity_data_list.append(cell)


    def append_current_data_to_file(self, output_file="simulation_data.json"):
        data_entry = {
            "timestamp": self.env.now,
            "entities": [self.convert_cell_to_dict(cell) for cell in self.saving_entity_data_list]
        }

        if not os.path.exists(output_file):
            with open(output_file, "w") as f:
                json.dump([], f)

        with open(output_file, "r") as f:
            data = json.load(f)

        data.append(data_entry)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
