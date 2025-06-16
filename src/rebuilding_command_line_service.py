import json

import pandas as pd

from src import RESOURCES
from src.production.production import Production
from src.provide_input_data.order_service import OrderService
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.simulation_environmnent.rebuilding_environment_simulation import RebuildingEnvironmentSimulation


class RebuildingCommandLineService:
    data_process_starting_conditions: pd.DataFrame
    pre_selected_visualisation_modus: str  # "y" or "n"

    def __init__(self, control_time: int):
        self.change_starting_condition_to_visualize_layout()
        self.order_service = OrderService()

        self.rebuilding_environment_simulation = RebuildingEnvironmentSimulation(self.order_service, control_time)
        self.service_starting_conditions = StartingConditionsService()
        self.production = Production(self.rebuilding_environment_simulation, self.service_starting_conditions)

    def start_simulation(self):
        simulation_duration = self.production.service_starting_conditions.set_simulation_duration_per_day()
        self.rebuilding_environment_simulation.initialise_simulation_start()
        self.rebuilding_environment_simulation.run_simulation(until=200000)
        self.change_back_starting_condition_to_visualize_layout()

    def change_starting_condition_to_visualize_layout(self):
        with open(RESOURCES / "simulation_starting_conditions.json", 'r', encoding='utf-8') as psc:
            self.data_process_starting_conditions = json.load(psc)
        self.pre_selected_visualisation_modus = self.data_process_starting_conditions["visualising_via_pygame(y/n)"]
        self.data_process_starting_conditions["visualising_via_pygame(y/n)"] = "y"

        with open(RESOURCES / "simulation_starting_conditions.json", "w", encoding="utf-8") as f:
            json.dump(self.data_process_starting_conditions, f, indent=4, ensure_ascii=False)

    def change_back_starting_condition_to_visualize_layout(self):
        with open(RESOURCES / "simulation_starting_conditions.json", 'r', encoding='utf-8') as psc:
            self.data_process_starting_conditions = json.load(psc)

        self.data_process_starting_conditions["visualising_via_pygame(y/n)"] = self.pre_selected_visualisation_modus

        with open(RESOURCES / "simulation_starting_conditions.json", "w", encoding="utf-8") as f:
            json.dump(self.data_process_starting_conditions, f, indent=4, ensure_ascii=False)
