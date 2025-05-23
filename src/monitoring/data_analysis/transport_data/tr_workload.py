import json
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt

from src.monitoring.data_analysis.creating_tr_during_simulation_dict import CreatingTrDuringSimulationDict
from src import TR_STATISTICS


class TrWorkload:
    workload_dict: dict[str, dict[str, int]]  # dict[tr.identification_str, dict[status, time]]

    def __init__(self, creating_tr_during_simulation_dict: CreatingTrDuringSimulationDict,
                 start_time: int | None = None, end_time: int | None = None):

        self.creating_tr_during_simulation_dict = creating_tr_during_simulation_dict
        self.every_tr_during_simulation_data = creating_tr_during_simulation_dict.every_tr_during_simulation_data
        self.tr_identification_str_list = creating_tr_during_simulation_dict.every_tr_identification_str_list

        self.start_time = start_time
        self.end_time = end_time

        self.workload_dict = {}

        self.delete_all_tr_statistics_files()
        self.calculate_workload()

    def save_workload_statistics(self):
        self.save_workload_to_json()
        self.create_pie_charts()

    def calculate_workload(self):
        # Status-Gruppierung
        status_group_map = {
            "MOVING_TO_PICKUP": "In Bewegung",
            "MOVING_TO_DROP_OFF": "In Bewegung",
            "RETURNING": "In Bewegung",
            "LOADING": "Be- und Entladen",
            "UNLOADING": "Be- und Entladen",
            "IDLE": "Wartend",
            "PAUSED": "Wartend"
        }

        for tr_id in self.tr_identification_str_list:
            status_times = defaultdict(float)
            tr_data = self.every_tr_during_simulation_data[tr_id]

            previous_timestamp = None
            previous_status = None

            for entry in tr_data:
                timestamp = entry['timestamp']

                # Filter nach Zeitraum (wenn gesetzt)
                if self.start_time is not None and timestamp < self.start_time:
                    continue
                if self.end_time is not None and timestamp > self.end_time:
                    continue

                entities = entry['entities']
                for entity in entities:
                    entity_data = entity['entity_data']
                    identification_str = entity_data['identification_str']
                    if identification_str == tr_id:
                        working_status = entity_data['working_status']
                        raw_status = working_status['status']
                        grouped_status = status_group_map.get(raw_status, raw_status)

                        if previous_status is None:
                            previous_status = grouped_status
                        elif previous_status != grouped_status:
                            if previous_timestamp is not None:
                                duration = timestamp - previous_timestamp
                                status_times[previous_status] += duration
                            previous_timestamp = timestamp
                            previous_status = grouped_status

                        if previous_timestamp is not None and previous_status is not None:
                            duration = timestamp - previous_timestamp
                            status_times[previous_status] += duration

                        previous_timestamp = timestamp
                        previous_status = grouped_status
                        break

            self.workload_dict[tr_id] = dict(status_times)

    def save_workload_to_json(self):
        json_file = TR_STATISTICS / 'tr_workload.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.workload_dict, f, indent=4)
        print(self.workload_dict)

    def create_pie_charts(self):
        # Definierte Farben als RGB (normiert)
        color_list = [
            (116 / 255, 33 / 255, 40 / 255),
            (161 / 255, 204 / 255, 201 / 255),
            (219 / 255, 203 / 255, 150 / 255),
            (191 / 255, 194 / 255, 186 / 255),
            (207 / 255, 171 / 255, 140 / 255),
            (146 / 255, 175 / 255, 204 / 255),
            (177 / 255, 153 / 255, 174 / 255)
        ]

        for tr_id, status_times in self.workload_dict.items():
            labels = list(status_times.keys())
            sizes = list(status_times.values())
            total = sum(sizes)

            if total == 0:
                print(f"[Info] Kein Zeitanteil für {tr_id}, kein Diagramm erzeugt.")
                continue

            sizes = [s / total * 100 for s in sizes]  # Prozentuale Darstellung
            colors = [color_list[i % len(color_list)] for i in range(len(labels))]

            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            plt.title(f'{tr_id} - Statusverteilung')  # tr_id enthält bereits 'TR: 1' etc.
            plt.axis('equal')

            safe_tr_id = tr_id.replace(":", "-").replace(" ", "_")
            chart_file = TR_STATISTICS / f'{safe_tr_id}_status_pie_chart.png'
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"[OK] Diagramm gespeichert unter: {chart_file}")

    def delete_all_tr_statistics_files(self):
        for file in TR_STATISTICS.iterdir():
            if file.is_file() and (file.suffix == '.png' or file.suffix == '.json'):
                try:
                    file.unlink()
                    print(f"[OK] Datei gelöscht: {file.name}")
                except Exception as e:
                    print(f"[Fehler] Konnte {file.name} nicht löschen: {e}")
