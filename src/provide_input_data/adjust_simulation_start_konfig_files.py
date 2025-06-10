import json
import pathlib

from src import RESOURCES


class AdjustSimulationStartKonfigFiles:
    data_process_starting_conditions: dict[str, str | int]
    file_path_list = list[pathlib.Path]

    def __init__(self):
        self.data_process_starting_conditions = None
        self.data_tr_conditions = None
        self.get_starting_condition_files_for_init()
        self.file_path_list = [RESOURCES / "simulation_starting_conditions.json",
                               RESOURCES / "simulation_production_transport_robot_data.json"]

    def run(self):
        self.delete_old_starting_condition_files()

    def get_starting_condition_files_for_init(self):
        with open(RESOURCES / "simulation_starting_conditions.json", 'r', encoding='utf-8') as psc:
            self.data_process_starting_conditions = json.load(psc)
        with open(RESOURCES / "simulation_production_transport_robot_data.json", 'r', encoding='utf-8') as psc:
            self.data_tr_conditions = json.load(psc)

    def delete_old_starting_condition_files(self):
        for file_path in self.file_path_list:
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Fehler beim Löschen von {file_path.name}: {e}")

    def save_new_starting_condition_files(self):
        with open(RESOURCES / "simulation_starting_conditions.json", "w", encoding="utf-8") as f:
            json.dump(self.data_process_starting_conditions, f, indent=4, ensure_ascii=False)

        with open(RESOURCES / "simulation_production_transport_robot_data.json", "w", encoding="utf-8") as g:
            json.dump(self.data_tr_conditions, g, indent=4, ensure_ascii=False)

    def set_new_topology_manager(self, topology_manager: int):
        self.data_process_starting_conditions[
            "Topology_manager(No algorithm (1), QAP (2), GA (3), FDP(4)"] = topology_manager

    def set_new_simulation_duration(self, days: str):
        self.data_process_starting_conditions["simulation_duration_in_days"] = days


    def set_new_visualisation_via_pygame(self, visualisation_decision: bool):
        if visualisation_decision is True:
            self.data_process_starting_conditions["visualising_via_pygame(y/n)"] = "y"
        else:
            self.data_process_starting_conditions["visualising_via_pygame(y/n)"] = "n"

