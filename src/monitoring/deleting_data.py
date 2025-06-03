import pathlib

from src import SIMULATION_OUTPUT_DATA, MACHINES_DURING_SIMULATION_DATA, SINK_DURING_SIMULATION_DATA, \
    WR_DURING_SIMULATION_DATA, TR_DURING_SIMULATION_DATA, INTERMEDIATE_STORE_DURING_SIMULATION_DATA, DAILY_PLANS, \
    GRAPH_PRODUCTION_MATERIAL, MACHINE_STATISTICS, MACHINE_STATISTICS_GRAPH, TR_STATISTICS, ANALYSIS_SOLUTION, \
    FORCED_DIRECTED_PLACEMENT, GENETIC_ALGORITHM, PRODUCTION_TOPOLOGY, WR_STATISTICS, MACHINE_WORKLOAD, PRODUCT_TRANSPORTING_TIME


class DeletingData:
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

        self.delete_json_data_in_path(FORCED_DIRECTED_PLACEMENT)
        self.delete_png_data_in_path(FORCED_DIRECTED_PLACEMENT)

        self.delete_json_data_in_path(GENETIC_ALGORITHM)
        self.delete_png_data_in_path(GENETIC_ALGORITHM)

        self.delete_png_data_in_path(PRODUCTION_TOPOLOGY)

    def delete_analysis_data(self):
        self.delete_every_analysis_data_json()
        self.delete_analysis_data_png()
        self.delete_analysis_data_xlsx()

    def delete_every_analysis_data_json(self):
        self.delete_json_data_in_path(TR_STATISTICS)
        self.delete_json_data_in_path(WR_STATISTICS)
        self.delete_json_data_in_path(ANALYSIS_SOLUTION)
        self.delete_json_data_in_path(MACHINE_WORKLOAD)
        self.delete_json_data_in_path(GRAPH_PRODUCTION_MATERIAL)
        self.delete_json_data_in_path(PRODUCT_TRANSPORTING_TIME)


    def delete_analysis_data_png(self):
        self.delete_png_data_in_path(GRAPH_PRODUCTION_MATERIAL)
        self.delete_png_data_in_path(MACHINE_STATISTICS_GRAPH)
        self.delete_png_data_in_path(TR_STATISTICS)
        self.delete_png_data_in_path(WR_STATISTICS)
        self.delete_png_data_in_path(ANALYSIS_SOLUTION)
        self.delete_png_data_in_path(MACHINE_WORKLOAD)
        self.delete_png_data_in_path(PRODUCT_TRANSPORTING_TIME)

    def delete_analysis_data_xlsx(self):
        self.delete_xlsx_data_in_path(MACHINE_STATISTICS)

    def delete_json_data_in_path(self, path: pathlib.Path):

        json_files = list(path.glob("*.json"))
        for file_path in json_files:
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Fehler beim Löschen von {file_path.name}: {e}")

    def delete_png_data_in_path(self, path: pathlib.Path):

        png_file = list(path.glob("*.png"))
        for file_path in png_file:
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Fehler beim Löschen von {file_path.name}: {e}")

    def delete_xlsx_data_in_path(self, path: pathlib.Path):

        xlsx_files = list(path.glob("*.xlsx"))
        for file_path in xlsx_files:
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Fehler beim Löschen von {file_path.name}: {e}")
