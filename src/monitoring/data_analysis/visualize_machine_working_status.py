import json
import re
import pandas as pd

from src import ENTITIES_DURING_SIMULATION_DATA


class VisualizeMachineWorkingStatus:
    def __init__(self, convert_json_data):
        self.convert_json_data = convert_json_data
        self.simulation_entity_df = self.convert_json_data.combined_simulation_entity_data_df

    def load_machine_simulation_data(self) -> pd.DataFrame:
        """
        Loads and combines all JSON files with machine data from the given folder
        and returns a DataFrame with only machine entities.
        """
        folder = ENTITIES_DURING_SIMULATION_DATA
        pattern = re.compile(r"simulation_run_data_from_(\d+)_sec_to_(\d+)_sec\.json")

        all_data = []
        file_info = []

        # Alle passenden Dateien im Ordner suchen und nach Startzeit sortieren
        for file in folder.glob("simulation_run_data_from_*_sec_to_*_sec.json"):
            match = pattern.match(file.name)
            if match:
                start_time = int(match.group(1))
                file_info.append((start_time, file))

        file_info.sort(key=lambda x: x[0])  # Nach Startzeit sortieren

        # JSON-Dateien lesen und nur Maschinen extrahieren
        for _, file in file_info:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

                for entry in data:
                    if isinstance(entry, dict) and 'entities' in entry:
                        for entity in entry['entities']:
                            # Überprüfe, ob 'entity_type' = "Machine" im Entitäts-Datenbereich vorhanden ist
                            if entity.get('entity_type') == 'Machine':
                                all_data.append(entry)

        return pd.DataFrame(all_data)

    def print(self):
        self.simulation_entity_df = self.load_machine_simulation_data()
        print(self.simulation_entity_df)
