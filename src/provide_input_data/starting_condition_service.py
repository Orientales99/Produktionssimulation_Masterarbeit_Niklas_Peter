import json
from datetime import date, datetime

from src import RESOURCES
from src.production.base.coordinates import Coordinates


class StartingConditionsService:

    def __init__(self):
        self.data_process_starting_conditions = None
        self.date_information = None
        self.get_starting_condition_files_for_init()


    def get_starting_condition_files_for_init(self):
        with open(RESOURCES / "simulation_starting_conditions.json", 'r', encoding='utf-8') as psc:
            self.data_process_starting_conditions = json.load(psc)
        with open(RESOURCES / "date_list.json", 'r', encoding='utf-8') as d:
            self.date_information = json.load(d)

    def get_date_list(self) -> list[date]:
        """Converts the loaded JSON list with strings into real datetime.date objects."""
        return [datetime.strptime(datum_str, "%Y-%m-%d").date() for datum_str in self.date_information]

    def set_max_coordinates_for_production_layout(self) -> Coordinates:
        return Coordinates(int(self.data_process_starting_conditions["production_layout_size_x"]),
                           int(self.data_process_starting_conditions["production_layout_size_y"]))

    def set_simulation_duration_per_day(self):
        duration_per_day_in_h = int(self.data_process_starting_conditions["production_day_duration_in_h"])
        total_duration = duration_per_day_in_h * 60 * 60
        return total_duration

    def set_starting_date_of_simulation(self) -> date:
        start_date_list = self.data_process_starting_conditions["starting_date_of_simulation"]
        starting_date = date(start_date_list[0], start_date_list[1], start_date_list[2])
        return starting_date

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

    def set_visualising_via_pygames(self):
        if self.data_process_starting_conditions["visualising_via_pygame(y/n)"] == "y":
            return True
        else:
            return False

