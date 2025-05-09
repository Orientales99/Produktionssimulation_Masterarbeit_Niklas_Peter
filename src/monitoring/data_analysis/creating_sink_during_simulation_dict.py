import pandas as pd
from src.monitoring.data_analysis.convert_json_data import ConvertJsonData


class CreatingSinkDuringSimulationDict:
    def __init__(self, convert_json_data: ConvertJsonData):
        self.convert_json_data = convert_json_data

        self.simulation_sink_df = self.convert_json_data.simulation_sink_data_df
        self.every_sink_status_during_simulation_data = []

        self.create_sorted_sink_list()

    def create_sorted_sink_list(self):
        """
        Erstellt eine Liste aller Sink-Zustände über die Simulation hinweg,
        sortiert nach dem Zeitstempel.
        """
        sink_list = self.extract_all_sink_entries()
        sink_list = self.sort_by_timestamp(sink_list)
        self.every_sink_status_during_simulation_data = sink_list

    def extract_all_sink_entries(self) -> list[dict]:
        """
        Durchläuft das DataFrame und extrahiert alle Zellen mit Sink-Daten.
        Gibt eine Liste aller relevanten Dicts zurück (je mit 'timestamp', 'entities').
        """
        sink_entries = []

        for _, row in self.simulation_sink_df.iterrows():
            for col in range(self.simulation_sink_df.shape[1]):
                cell_data = row[col]
                if cell_data and isinstance(cell_data, dict):
                    entities = cell_data["entities"]
                    for entity in entities:
                        if entity["entity_type"] == 'Sink':
                            sink_entries.append(cell_data)
                            break  # Pro Zelle reicht ein Sink

        return sink_entries

    def sort_by_timestamp(self, entries: list[dict]) -> list[dict]:
        """
        Sortiert die Einträge nach dem Feld 'timestamp'.
        """
        return sorted(entries, key=lambda x: x.get('timestamp', float('inf')))
