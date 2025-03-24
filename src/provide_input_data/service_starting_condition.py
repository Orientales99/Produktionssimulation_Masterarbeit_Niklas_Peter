import json
from src import RESOURCES
from src.production.base.coordinates import Coordinates


class ServiceStartingConditions:

    def __init__(self):
        self.data_process_starting_conditions = None
        self.get_starting_condition_files_for_init()

    def get_starting_condition_files_for_init(self):
        with open(RESOURCES / "simulation_starting_conditions.json", 'r', encoding='utf-8') as psc:
            self.data_process_starting_conditions = json.load(psc)

    def set_max_coordinates_for_production_layout(self) -> Coordinates:
        return Coordinates(int(self.data_process_starting_conditions["production_layout_size_x"]),
                           int(self.data_process_starting_conditions["production_layout_size_y"]))

    def set_visualising_via_terminal(self):
        if self.data_process_starting_conditions["visualising_via_terminal(y/n)"] == "y":
            return True
        else:
            return False

    def set_visualising_via_matplotlib(self):
        if self.data_process_starting_conditions["visualising_via_matplotlib(y/n)"] == "y":
            return True
        else:
            return False
