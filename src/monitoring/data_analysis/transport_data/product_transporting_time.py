import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
from src import PRODUCT_TRANSPORTING_TIME


class ProductTransportingTime:
    def __init__(self, creating_tr_during_simulation_dict):
        self.creating_tr_during_simulation_dict = creating_tr_during_simulation_dict
        self.every_tr_during_simulation_data = creating_tr_during_simulation_dict.every_tr_during_simulation_data
        self.tr_identification_str_list = creating_tr_during_simulation_dict.every_tr_identification_str_list

        os.makedirs(PRODUCT_TRANSPORTING_TIME, exist_ok=True)
        self.plot_color = "#742128"  # RGB (116, 33, 40)

    def calculate_transporting_time(self, start_time: int = 0, end_time: int = float('inf')):
        transport_durations = self.track_product_transport(start_time, end_time)

        avg_times = self.calculate_average_transport_time(transport_durations)
        self.save_transport_time_json(avg_times)
        self.plot_transport_times(avg_times)

        overall_avg = self.calculate_overall_average_time(transport_durations)
        self.save_total_average_time_json(overall_avg)

        self.save_cumulative_transport_times_json(transport_durations)
        self.plot_cumulative_transport_times(transport_durations)

    def filter_snapshots_by_time(self, snapshots, start_time, end_time):
        return [snap for snap in snapshots if start_time <= snap["timestamp"] <= end_time]

    def extract_loaded_products(self, entity_data):
        material_store = entity_data.get("material_store", {})
        contained_units = material_store.get("Contained Units", 0)
        loaded_products = material_store.get("Loaded Products", {})
        return contained_units, loaded_products

    def track_product_transport(self, start_time=0, end_time=float("inf")):
        product_transport_start = defaultdict(list)
        product_transport_durations = defaultdict(list)

        for tr_id in self.tr_identification_str_list:
            tr_snapshots = self.every_tr_during_simulation_data[tr_id]
            filtered_snapshots = self.filter_snapshots_by_time(tr_snapshots, start_time, end_time)

            previous_products = {}

            for snapshot in filtered_snapshots:
                timestamp = snapshot["timestamp"]
                for entity in snapshot["entities"]:
                    entity_data = entity["entity_data"]
                    contained_units, loaded_products = self.extract_loaded_products(entity_data)

                    if contained_units > 0 and loaded_products:
                        for full_name, quantity in loaded_products.items():
                            product_group = full_name.split(".")[1]

                            if previous_products.get(product_group) is None:
                                product_transport_start[product_group].append((timestamp, quantity))
                                previous_products[product_group] = True

                    elif contained_units == 0 and previous_products:
                        for product_group in list(previous_products.keys()):
                            if product_transport_start[product_group]:
                                start_time_product, quantity = product_transport_start[product_group].pop(0)
                                transport_time = timestamp - start_time_product
                                avg_time_per_unit = transport_time / quantity if quantity > 0 else 0
                                product_transport_durations[product_group].append(avg_time_per_unit)
                                previous_products.pop(product_group, None)

        return product_transport_durations

    def seconds_to_readable_time(self, seconds: float) -> str:
        seconds = int(round(seconds))
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02}:{m:02}:{s:02}"  # hh:mm:ss
        else:
            return f"{m:02}:{s:02}"  # mm:ss

    def calculate_average_transport_time(self, transport_durations):
        return {
            product: round(sum(times) / len(times), 2)
            for product, times in transport_durations.items()
            if times
        }

    def calculate_overall_average_time(self, transport_durations):
        all_times = [time for times in transport_durations.values() for time in times]
        return round(sum(all_times) / len(all_times), 2) if all_times else 0

    def save_transport_time_json(self, avg_times: dict):
        readable = {
            product: {
                "average_seconds": round(avg, 2),
            }
            for product, avg in avg_times.items()
        }
        path = os.path.join(PRODUCT_TRANSPORTING_TIME, "average_transporting_time.json")
        with open(path, "w") as f:
            json.dump(readable, f, indent=4)

    def save_total_average_time_json(self, overall_avg: float):
        # Für kumulierte Zeiten:
        cumulative_times = {
            product: sum(times)
            for product, times in self.track_product_transport().items()
        }

        total_cumulative_avg = (
            sum(cumulative_times.values()) / len(cumulative_times)
            if cumulative_times else 0
        )

        data = {
            "total_average_seconds": round(overall_avg, 2),
            "cumulative_average_seconds": round(total_cumulative_avg, 2),
            "cumulative_average_time": self.seconds_to_readable_time(total_cumulative_avg)
        }

        path = os.path.join(PRODUCT_TRANSPORTING_TIME, "total_average_transporting_time.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    def save_cumulative_transport_times_json(self, transport_durations: dict):
        cumulative_times = {
            product: {
                "cumulative_seconds": round(sum(times), 2),
                "cumulative_time": self.seconds_to_readable_time(sum(times))
            }
            for product, times in transport_durations.items()
        }
        path = os.path.join(PRODUCT_TRANSPORTING_TIME, "cumulative_transporting_time.json")
        with open(path, "w") as f:
            json.dump(cumulative_times, f, indent=4)

    def plot_transport_times(self, avg_times: dict):
        plt.figure(figsize=(10, 6))
        products = list(avg_times.keys())
        values = list(avg_times.values())

        plt.bar(products, values, color=self.plot_color)
        plt.xlabel("Produktgruppe")
        plt.ylabel("∅ Transportzeit pro Einheit")
        plt.title("Durchschnittliche Transportzeit pro Produkt")
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        plt_path = os.path.join(PRODUCT_TRANSPORTING_TIME, "average_transporting_time.png")
        plt.savefig(plt_path)
        plt.close()

    def plot_cumulative_transport_times(self, transport_durations: dict):
        cumulative_times = {
            product: round(sum(times), 2)
            for product, times in transport_durations.items()
        }

        products = list(cumulative_times.keys())
        values = list(cumulative_times.values())

        plt.figure(figsize=(10, 6))
        plt.bar(products, values, color=self.plot_color)
        plt.xlabel("Produktgruppe")
        plt.ylabel("Kumulierte Transportzeit")
        plt.title("Kumulierte Transportzeit pro Produkt")
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        plt_path = os.path.join(PRODUCT_TRANSPORTING_TIME, "cumulative_transporting_time.png")
        plt.savefig(plt_path)
        plt.close()
