import json
from collections import defaultdict

import matplotlib.pyplot as plt

from src.monitoring.data_analysis.creating_machine_during_simulation_dict import CreatingMachineDuringSimulationDict
from src.constant.constant import MachineWorkingRobotStatus, MachineStorageStatus
from src import MACHINE_WORKLOAD


class MachineWorkload:
    workload_dict: dict[str, dict[str, int]]  # dict[machine_id, dict[status, time]]

    def __init__(self, creating_machine_during_simulation_dict: CreatingMachineDuringSimulationDict,
                 start_time: int | None = None, end_time: int | None = None):
        self.creating_machine_during_simulation_dict = creating_machine_during_simulation_dict
        self.every_machine_during_simulation_data = self.creating_machine_during_simulation_dict.every_machine_during_simulation_data
        self.machine_identification_str_list = self.creating_machine_during_simulation_dict.every_machine_identification_str_list

        self.start_time = start_time
        self.end_time = end_time

        self.workload_dict = {}


        self.calculate_workload()

    def save_workload_statistics(self):
        self.save_workload_to_json()
        self.create_pie_charts()

    def calculate_workload(self):
        for machine_id in self.machine_identification_str_list:
            status_times = self._calculate_status_times_for_machine(machine_id)
            self.workload_dict[machine_id] = self._group_statuses(status_times)

    def _calculate_status_times_for_machine(self, machine_id: str) -> dict[str, float]:
        status_times = defaultdict(float)
        previous_timestamp = None
        previous_status = None

        for entry in self.every_machine_during_simulation_data[machine_id]:
            timestamp = entry["timestamp"]
            if not self._is_timestamp_in_range(timestamp):
                continue

            status = self._extract_grouped_status(entry, machine_id)
            if status is None:
                continue

            if previous_status is None:
                previous_status = status
                previous_timestamp = timestamp
                continue

            duration = timestamp - previous_timestamp
            status_times[previous_status] += duration

            previous_timestamp = timestamp
            previous_status = status

        return status_times

    def _is_timestamp_in_range(self, timestamp: int) -> bool:
        if self.start_time is not None and timestamp < self.start_time:
            return False
        if self.end_time is not None and timestamp > self.end_time:
            return False
        return True

    def _extract_grouped_status(self, entry: dict, machine_id: str) -> str | None:
        for entity in entry["entities"]:
            entity_data = entity["entity_data"]
            if entity_data["identification_str"] != machine_id:
                continue

            wr_status = entity_data["working_status"]["working_robot_status"]
            storage_status = entity_data["working_status"]["storage_status"]
            processing_list = entity_data["Processing Order List"]

            return self._group_status(wr_status, storage_status, processing_list)
        return None

    def _group_status(self, wr_status: str, storage_status: str, processing_list: list) -> str:
        if wr_status == MachineWorkingRobotStatus.WR_PRESENT.value:
            if storage_status == MachineStorageStatus.STORAGES_READY_FOR_PRODUCTION.value:
                return "Produziert Material"
            elif storage_status == MachineStorageStatus.INPUT_EMPTY.value:
                return "Wartet auf Material"
            elif storage_status == MachineStorageStatus.OUTPUT_FULL.value:
                return "Wartet auf Abholung"
            else:
                return "Sonstige (mit WR)"
        elif wr_status in [MachineWorkingRobotStatus.NO_WR.value,
                           MachineWorkingRobotStatus.WAITING_WR.value,
                           MachineWorkingRobotStatus.WR_LEAVING.value]:
            if len(processing_list) == 0:
                return "Hat keinen Auftrag"
            else:
                return "Wartet auf WR"
        return "Unbekannt"

    def _group_statuses(self, status_times: dict[str, float]) -> dict[str, float]:
        groups = {
            "Produktion": ["Produziert Material"],
            "Wartet auf Material": ["Wartet auf Material"],
            "Wartet auf Abholung": ["Wartet auf Abholung"],
            "Leerlauf": ["Hat keinen Auftrag"],
            "Wartet auf WR": ["Wartet auf WR"],
            "Sonstige": ["Sonstige (mit WR)", "Unbekannt"]
        }

        grouped = defaultdict(float)
        for group, statuses in groups.items():
            for status in statuses:
                grouped[group] += status_times.get(status, 0.0)

        # Entferne alle Gruppen mit Zeitanteil 0.0
        filtered_grouped = {group: time for group, time in grouped.items() if time > 0.0}

        return filtered_grouped

    def save_workload_to_json(self):
        json_path = MACHINE_WORKLOAD / 'machine_workload_grouped.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.workload_dict, f, indent=4)

        print(f"[OK] Gruppierter Maschinen-Workload gespeichert unter: {json}")

    def create_pie_charts(self):
        for machine_id, status_times in self.workload_dict.items():
            self._create_single_pie_chart(machine_id, status_times, grouped=True)

    def _create_single_pie_chart(self, machine_id: str, status_times: dict[str, float], grouped: bool):
        total = sum(status_times.values())
        if total == 0:
            print(f"[Info] Kein Zeitanteil für {machine_id}, kein Diagramm erzeugt.")
            return

        labels, sizes = zip(*status_times.items())
        sizes = [s / total * 100 for s in sizes]
        colors = self._get_colors(len(labels))

        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title(f'{machine_id} - Statusverteilung')
        plt.axis('equal')

        safe_id = machine_id.replace(":", "-").replace(" ", "_")
        chart_file = MACHINE_WORKLOAD / f'{safe_id}_status_pie_chart.png'
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[OK] Diagramm gespeichert unter: {chart_file}")

    def _get_colors(self, count: int) -> list[tuple[float, float, float]]:
        base_colors = [
            (116 / 255, 33 / 255, 40 / 255),
            (161 / 255, 204 / 255, 201 / 255),
            (219 / 255, 203 / 255, 150 / 255),
            (191 / 255, 194 / 255, 186 / 255),
            (207 / 255, 171 / 255, 140 / 255),
            (146 / 255, 175 / 255, 204 / 255),
            (177 / 255, 153 / 255, 174 / 255)
        ]
        return [base_colors[i % len(base_colors)] for i in range(count)]
