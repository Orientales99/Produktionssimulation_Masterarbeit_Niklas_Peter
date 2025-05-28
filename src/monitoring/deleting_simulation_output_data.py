import pathlib

from src import SIMULATION_OUTPUT_DATA, MACHINES_DURING_SIMULATION_DATA, SINK_DURING_SIMULATION_DATA, WR_DURING_SIMULATION_DATA, TR_DURING_SIMULATION_DATA, INTERMEDIATE_STORE_DURING_SIMULATION_DATA, DAILY_PLANS


class DeletingSimulationOutputData:
    def __init__(self):
        pass

    def delete_every_simulation_output_data_json(self):
        self.delete_json_data_in_path(SIMULATION_OUTPUT_DATA)
        self.delete_json_data_in_path(DAILY_PLANS)

        self.delete_json_data_in_path(MACHINES_DURING_SIMULATION_DATA)
        self.delete_json_data_in_path(WR_DURING_SIMULATION_DATA)
        self.delete_json_data_in_path(TR_DURING_SIMULATION_DATA)
        self.delete_json_data_in_path(INTERMEDIATE_STORE_DURING_SIMULATION_DATA)
        self.delete_json_data_in_path(SINK_DURING_SIMULATION_DATA)

    def delete_json_data_in_path(self, path: pathlib.Path):

        json_files = list(path.glob("*.json"))
        for file_path in json_files:
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Fehler beim Löschen von {file_path.name}: {e}")


