import json
from collections import defaultdict
import matplotlib.pyplot as plt

from src.monitoring.data_analysis.creating_wr_during_simulation_dict import CreatingWrDuringSimulationDict
from src.constant.constant import WorkingRobotStatus
from src import WR_STATISTICS


class WrWorkload:
    workload_dict: dict[str, dict[str, int]]  # dict[tr.identification_str, dict[status, time]]

    def __init__(self, creating_wr_during_simulation_dict: CreatingWrDuringSimulationDict,
                        start_time: int | None = None, end_time: int | None = None):

        self.creating_wr_during_simulation_dict = creating_wr_during_simulation_dict
        self.every_wr_during_simulation_data = self.creating_wr_during_simulation_dict.every_wr_during_simulation_data
        self.wr_identification_str_list = self.creating_wr_during_simulation_dict.every_wr_identification_str_list

        self.start_time = start_time
        self.end_time = end_time

        self.workload_dict = {}

        self.calculate_workload()

    def save_workload_statistics(self):
        self.save_workload_to_json()
        self.create_pie_charts()

    def calculate_workload(self):
        status_group_map = {
            "IDLE": "Wartend",
            "WAITING_FOR_ORDER": "Wartend",
            "PAUSED": "Wartend",
            "WORKING_ON_MACHINE": "In Arbeit (in Maschine)",
            "WAITING_IN_FRONT_OF_MACHINE": "In Arbeit (in Maschine)",
            "MOVING_TO_MACHINE": "In Bewegung",
            "RETURNING": "In Bewegung"
        }

        for wr_id in self.wr_identification_str_list:
            status_times = defaultdict(float)
            wr_data = self.every_wr_during_simulation_data[wr_id]

            previous_timestamp = None
            previous_status = None

            for entry in wr_data:
                timestamp = entry['timestamp']
                if self.start_time is not None and timestamp < self.start_time:
                    continue
                if self.end_time is not None and timestamp > self.end_time:
                    continue

                for entity in entry['entities']:
                    entity_data = entity['entity_data']
                    identification_str = entity_data['identification_str']
                    if identification_str == wr_id:
                        raw_status = entity_data['working_status']['status']
                        grouped_status = status_group_map.get(raw_status, "Sonstige")

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

            self.workload_dict[wr_id] = dict(status_times)

    def save_workload_to_json(self):
        json_file = WR_STATISTICS / 'wr_workload.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.workload_dict, f, indent=4)
        print("[OK] WR-Workload JSON gespeichert:", json_file)

    def create_pie_charts(self):
        color_list = [
            (116 / 255, 33 / 255, 40 / 255),  # Leuphanarot
            (161 / 255, 204 / 255, 201 / 255),  # Grau
            (219 / 255, 203 / 255, 150 / 255),  # Beige
        ]

        for wr_id, status_times in self.workload_dict.items():
            labels = list(status_times.keys())
            sizes = list(status_times.values())
            total = sum(sizes)

            if total == 0:
                print(f"[Info] Kein Zeitanteil für {wr_id}, kein Diagramm erzeugt.")
                continue

            sizes = [s / total * 100 for s in sizes]
            colors = [color_list[i % len(color_list)] for i in range(len(labels))]

            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            plt.title(f'{wr_id} – Statusverteilung')
            plt.axis('equal')

            safe_wr_id = wr_id.replace(":", "-").replace(" ", "_")
            chart_file = WR_STATISTICS / f'{safe_wr_id}_status_pie_chart.png'
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"[OK] Diagramm gespeichert unter: {chart_file}")
