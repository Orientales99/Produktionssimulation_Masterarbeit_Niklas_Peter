from src.monitoring.data_analysis.creating_intermediate_store_during_simulation_dict import \
    CreatingIntermediateStoreDuringSimulationDict
from src.monitoring.data_analysis.creating_machine_during_simulation_dict import CreatingMachineDuringSimulationDict
from src.monitoring.data_analysis.creating_tr_during_simulation_dict import CreatingTrDuringSimulationDict


class MaterialFlow:
    object_material_flow_matrix: dict[str, dict[str, int]] = {}

    def __init__(self, creating_tr_during_simulation_dict: CreatingTrDuringSimulationDict,
                 creating_machine_during_simulation_dict: CreatingMachineDuringSimulationDict,
                 creating_intermediate_store_during_simulation_dict: CreatingIntermediateStoreDuringSimulationDict):

        self.creating_tr_during_simulation_dict = creating_tr_during_simulation_dict

        self.every_tr_during_simulation_data = self.creating_tr_during_simulation_dict.every_tr_during_simulation_data

        self.tr_identification_str_list = self.creating_tr_during_simulation_dict.every_tr_identification_str_list

        self.creating_machine_during_simulation_dict = creating_machine_during_simulation_dict

        self.machine_identification_str_list = self.creating_machine_during_simulation_dict.every_machine_identification_str_list

        self.creating_intermediate_store_during_simulation_dict = creating_intermediate_store_during_simulation_dict

        self.intermediate_store_identification_str_list = self.creating_intermediate_store_during_simulation_dict.every_intermediate_store_identification_str_list

        self.object_material_flow_matrix = {}

    def create_material_flow_matrix(self, start_time: int = 0, end_time: int = float('inf')) -> dict[
        str, dict[str, int]]:
        """Creates a matrix of material flows with optional time filtering, including all known entities."""
        all_stations = set()

        # Alle TR-Daten durchgehen und beteiligte Stationen erfassen
        for tr_id in self.tr_identification_str_list:
            tr_snapshots = self.every_tr_during_simulation_data[tr_id]
            filtered_snapshots = self.filter_snapshots_by_time(tr_snapshots, start_time, end_time)

            for snapshot in filtered_snapshots:
                for entity in snapshot["entities"]:
                    entity_data = entity["entity_data"]
                    transport_order = entity_data["transport_order"]
                    from_station = transport_order["pick up station"]
                    to_station = transport_order["unload destination"]
                    if from_station:
                        all_stations.add(from_station)
                    if to_station:
                        all_stations.add(to_station)

        # Ergänze alle bekannten Maschinen und Intermediate Stores
        all_stations.update(self.machine_identification_str_list)
        all_stations.update(self.intermediate_store_identification_str_list)

        # Matrix vorbereiten: Alle Stationen als Zeilen und Spalten eintragen
        for station in all_stations:
            if station not in self.object_material_flow_matrix:
                self.object_material_flow_matrix[station] = {}
            for target in all_stations:
                if target not in self.object_material_flow_matrix[station] and target != station:
                    self.object_material_flow_matrix[station][target] = 0

        # Materialflüsse eintragen
        for tr_id in self.tr_identification_str_list:
            tr_snapshots = self.every_tr_during_simulation_data[tr_id]
            filtered_snapshots = self.filter_snapshots_by_time(tr_snapshots, start_time, end_time)
            last_counted_order = None

            for snapshot in filtered_snapshots:
                for entity in snapshot["entities"]:
                    entity_data = entity["entity_data"]
                    transport_order = entity_data["transport_order"]
                    working_status = entity_data["working_status"]
                    from_station = transport_order["pick up station"]
                    to_station = transport_order["unload destination"]
                    quantity = transport_order["quantity"]
                    status = working_status["status"]
                    current_order = (from_station, to_station, quantity)

                    if not self.is_valid_transport_order(from_station, to_station, quantity):
                        continue

                    if self.is_new_and_completed_order(current_order, last_counted_order, quantity):
                        self.object_material_flow_matrix[from_station][to_station] += quantity
                        last_counted_order = current_order
                    elif current_order != last_counted_order and quantity == 0:
                        last_counted_order = current_order

        return self.object_material_flow_matrix

    def filter_snapshots_by_time(self, snapshots: list[dict], start: int, end: int) -> list[dict]:
        """Filters snapshots within a time range."""
        return [s for s in snapshots if start <= s["timestamp"] <= end]

    def is_valid_transport_order(self, from_station: str, to_station: str, quantity: int) -> bool:
        """Checks whether a transport order makes sense."""
        return bool(from_station and to_station and quantity >= 0)

    def is_new_and_completed_order(self, current_order, last_order, quantity) -> bool:
        """Checks whether there is a new and completed transport"""
        return current_order != last_order and quantity > 0

    def add_to_flow_matrix(self, from_station: str, to_station: str, quantity: int) -> None:
        """Adds material flow to the matrix."""
        if from_station not in self.object_material_flow_matrix:
            self.object_material_flow_matrix[from_station] = {}
        if to_station not in self.object_material_flow_matrix[from_station]:
            self.object_material_flow_matrix[from_station][to_station] = 0
        self.object_material_flow_matrix[from_station][to_station] += quantity
