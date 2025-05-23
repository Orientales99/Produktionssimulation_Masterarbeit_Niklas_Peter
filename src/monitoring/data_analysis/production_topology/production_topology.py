from matplotlib import pyplot as plt

from src.monitoring.data_analysis.creating_intermediate_store_during_simulation_dict import \
    CreatingIntermediateStoreDuringSimulationDict
from src.monitoring.data_analysis.creating_machine_during_simulation_dict import CreatingMachineDuringSimulationDict
from src import PRODUCTION_TOPOLOGY


class ProductionTopology:
    creating_machine_during_simulation_dict: CreatingMachineDuringSimulationDict
    creating_intermediate_store_during_simulation_dict: CreatingIntermediateStoreDuringSimulationDict

    entity_position_dict = list[dict[str, int, int]] # dict[identification_str, x, y]

    def __init__(self, creating_machine_during_simulation_dict, creating_intermediate_store_during_simulation_dict):
        self.creating_machine_during_simulation_dict = creating_machine_during_simulation_dict
        self.every_machine_during_simulation_data = self.creating_machine_during_simulation_dict.every_machine_during_simulation_data
        self.machine_identification_str_list = self.creating_machine_during_simulation_dict.every_machine_identification_str_list

        self.creating_intermediate_store_during_simulation_dict = creating_intermediate_store_during_simulation_dict
        self.every_intermediate_store_during_simulation_data = self.creating_intermediate_store_during_simulation_dict.every_intermediate_store_during_simulation_data
        self.intermediate_store_identification_str_list = self.creating_intermediate_store_during_simulation_dict.every_intermediate_store_identification_str_list

        self.delete_all_pngs_in_directory()

        self.entity_position_dict = []

    def start_plot_production_topology(self):
        self.build_entity_position_snapshots()
        self.plot_all_tags()

    def build_entity_position_snapshots(self):
        combined_data = []
        for data in self.every_machine_during_simulation_data.values():
            combined_data.extend(data)
        for data in self.every_intermediate_store_during_simulation_data.values():
            combined_data.extend(data)
        combined_data.sort(key=lambda entry: entry['timestamp'])

        snapshot_times = set()
        max_timestamp = combined_data[-1]['timestamp'] if combined_data else 0
        i = 0
        while True:
            t = 6000 if i == 0 else 29000 * i
            if t > max_timestamp:
                break
            snapshot_times.add(t)
            i += 1
        snapshot_times = sorted(snapshot_times)

        self.entity_position_dict = []
        last_known_positions: dict[str, dict] = {}
        data_index = 0

        for snapshot_time in snapshot_times:
            while data_index < len(combined_data) and combined_data[data_index]['timestamp'] <= snapshot_time:
                entry = combined_data[data_index]
                for entity in entry.get('entities', []):
                    ident = entity['entity_data']['identification_str']
                    last_known_positions[ident] = {
                        'x': entity['x'],
                        'y': entity['y'],
                        'type': entity['entity_type']
                    }
                data_index += 1

            snapshot_positions = {}
            for ident in self.machine_identification_str_list:
                if ident in last_known_positions:
                    snapshot_positions[ident] = last_known_positions[ident]
            for ident in self.intermediate_store_identification_str_list:
                if ident in last_known_positions:
                    snapshot_positions[ident] = last_known_positions[ident]

            snapshot = {
                'tag': f"Tag {len(self.entity_position_dict) + 1}",
                'timestamp': snapshot_time,
                'positions': snapshot_positions
            }
            self.entity_position_dict.append(snapshot)

    def plot_all_tags(self):
        for snapshot in self.entity_position_dict:
            self.plot_positions(snapshot["positions"], snapshot["tag"])

    def plot_positions(self, position_dict: dict, tag_label: str):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 10))

        # Farbcodes als RGB normalisiert
        machine_color = (116 / 255, 33 / 255, 40 / 255)
        store_color = (161 / 255, 204 / 255, 201 / 255)

        for ident_str, info in position_dict.items():
            x, y, typ = info["x"], info["y"], info["type"]
            if typ == 'Machine':
                color = machine_color
                label = "Maschine"
            else:
                color = store_color
                label = "Zwischenlager"

            # Nur ein Label pro Typ (verhindert Duplikate in der Legende)
            already_labels = plt.gca().get_legend_handles_labels()[1]
            plt.scatter(x, y, c=[color], s=100, label=label if label not in already_labels else "")
            plt.text(x + 1, y + 1, ident_str, fontsize=9)

        plt.title(f"Produktionslayout – {tag_label}")
        plt.xlabel("x-Achse")
        plt.ylabel("y-Achse")
        plt.legend()
        plt.grid(True)
        plt.axis('equal')

        file_path = PRODUCTION_TOPOLOGY / f"Produktionstopologie_{tag_label}.png"
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()

    def delete_all_pngs_in_directory(self):
        deleted_files = 0
        for file in PRODUCTION_TOPOLOGY.glob("*.png"):
            try:
                file.unlink()
                deleted_files += 1
            except Exception as e:
                print(f"[Fehler] Konnte Datei nicht löschen: {file.name}, Fehler: {e}")
        print(f"[OK] {deleted_files} PNG-Datei(en) im Pfad '{PRODUCTION_TOPOLOGY}' gelöscht.")