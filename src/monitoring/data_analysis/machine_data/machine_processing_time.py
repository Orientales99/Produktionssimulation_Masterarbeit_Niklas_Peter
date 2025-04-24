import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from src import MACHINE_STATISTICS, MACHINE_STATISTICS_GRAPH


class MachineProcessingTime:
    every_machine_during_simulation_data: dict[str, list[dict]]
    machine_identification_str_list: list[str]
    machine_statistics_data: list

    def __init__(self, creating_machine_during_simulation_dict):
        self.creating_machine_during_simulation_dict = creating_machine_during_simulation_dict

        self.every_machine_during_simulation_data = self.creating_machine_during_simulation_dict.every_machine_during_simulation_data
        self.machine_identification_str_list = self.creating_machine_during_simulation_dict.every_machine_identification_str_list

        self.machine_statistics_data = []

        self.get_production_machine_data()
        # self.plot_mean_processing_times_per_machine()
        self.save_machine_statistics_table()

    def get_production_machine_data(self):

        for identification_str in self.machine_identification_str_list:
            machine_dict_list = self.every_machine_during_simulation_data.get(identification_str)

            unique_product_list = self.get_list_of_produced_product_group_for_machine(machine_dict_list)

            for product in unique_product_list:

                processing_time_per_product_list = self.get_list_processing_time_per_product(machine_dict_list, product)
                waiting_time_for_material_input_list = self.get_list_waiting_time_machine_input_empty(machine_dict_list, product)
                waiting_time_for_material_output_list = self.get_list_waiting_time_machine_output_full(machine_dict_list, product)

                self.machine_statistics_data.append({
                    "machine": identification_str,
                    "product": product,

                    "mean_processing_time": self.get_mean_duration(processing_time_per_product_list),
                    "std_dev_processing_time": self.get_std_dev_duration(processing_time_per_product_list),
                    "variance_processing_time": self.get_variance_duration(processing_time_per_product_list),

                    "mean_waiting_input_time": self.get_mean_duration(waiting_time_for_material_input_list),
                    "std_dev_waiting_input_time": self.get_std_dev_duration(waiting_time_for_material_input_list),
                    "variance_waiting_input_time": self.get_variance_duration(waiting_time_for_material_input_list),

                    "mean_waiting_output_time": self.get_mean_duration(waiting_time_for_material_output_list),
                    "std_dev_waiting_output_time": self.get_std_dev_duration(waiting_time_for_material_output_list),
                    "variance_waiting_output_time": self.get_variance_duration(waiting_time_for_material_output_list),
                })


    def get_list_of_produced_product_group_for_machine(self, machine_data_during_simulation: list[dict]) -> list[str]:
        """
        Input a list of dictionaries of one machine with every status change and timestamp. Creating a list of every
        product this machine has produced in the production
        :return list of str (product group: ex. "ProductGroup.THREE.1)"""
        unique_products = set()

        for entry in machine_data_during_simulation:
            for entity in entry.get("entities", []):
                if entity.get("entity_type") == "Machine":
                    material = entity.get("entity_data", {}).get("working_status", {}).get(
                        "producing_production_material")
                    if material:
                        unique_products.add(material)

        return list(unique_products)

    def get_list_processing_time_per_product(self, machine_data_during_simulation: list[dict], product_group: str) -> list[int]:
        """ Calculates processing durations for a specific product group based on machine status data over time.
        :return: A list of processing durations in time units."""

        processing_times = []
        is_processing = False
        start_time = None

        for entry in machine_data_during_simulation:
            timestamp = entry.get("timestamp")
            for entity in entry.get("entities", []):

                status = entity.get("entity_data", {}).get("working_status", {})
                current_material = status.get("producing_production_material")
                process_status = status.get("process_status")
                producing_item = status.get("producing_item")

                conditions_met = (
                    current_material == product_group and
                    process_status == "producing product" and
                    producing_item is True
                )

                if conditions_met and not is_processing:
                    # Mark starting point
                    start_time = timestamp
                    is_processing = True

                elif is_processing and (not conditions_met):
                    # Mark end point
                    end_time = timestamp
                    processing_times.append(end_time - start_time)
                    is_processing = False
                    start_time = None

        # If an ongoing process has not been completed at the end
        if is_processing and start_time is not None:
            end_time = machine_data_during_simulation[-1]["timestamp"]
            processing_times.append(end_time - start_time)

        return processing_times


    def get_list_waiting_time_machine_input_empty(self, machine_data_during_simulation: list[dict], product_group: str) -> list[int]:
        """ Calculates waiting for material input durations for a specific product group based on machine status data
            over time.
                :return: A list of waiting time ."""

        waiting_time_material_input_list = []
        is_processing = False
        start_time = None

        for entry in machine_data_during_simulation:
            timestamp = entry.get("timestamp")
            for entity in entry.get("entities", []):

                status = entity.get("entity_data", {}).get("working_status", {})
                current_material = status.get("producing_production_material")
                process_status = status.get("process_status")
                storage_status = status.get("storage_status")


                conditions_met = (
                        current_material == product_group and
                        process_status == "producing is paused" and
                        storage_status == "input storage is empty"
                )

                if conditions_met and not is_processing:
                    # Mark starting point
                    start_time = timestamp
                    is_processing = True

                elif is_processing and (not conditions_met):
                    # Mark end point
                    end_time = timestamp
                    waiting_time_material_input_list.append(end_time - start_time)
                    is_processing = False
                    start_time = None

        # If an ongoing process has not been completed at the end
        if is_processing and start_time is not None:
            end_time = machine_data_during_simulation[-1]["timestamp"]
            waiting_time_material_input_list.append(end_time - start_time)

        return waiting_time_material_input_list

    def get_list_waiting_time_machine_output_full(self, machine_data_during_simulation: list[dict], product_group: str) -> list[int]:
        """ Calculates waiting for material output durations for a specific product group based on machine status data
            over time.
                :return: A list of waiting time ."""

        waiting_time_material_output_list = []
        is_processing = False
        start_time = None

        for entry in machine_data_during_simulation:
            timestamp = entry.get("timestamp")
            for entity in entry.get("entities", []):

                status = entity.get("entity_data", {}).get("working_status", {})
                current_material = status.get("producing_production_material")
                storage_status = status.get("storage_status")

                conditions_met = (
                        current_material == product_group and
                        storage_status == "output storage is full"
                )

                if conditions_met and not is_processing:
                    # Mark starting point
                    start_time = timestamp
                    is_processing = True

                elif is_processing and (not conditions_met):
                    # Mark end point
                    end_time = timestamp
                    waiting_time_material_output_list.append(end_time - start_time)
                    is_processing = False
                    start_time = None

        # If an ongoing process has not been completed at the end
        if is_processing and start_time is not None:
            end_time = machine_data_during_simulation[-1]["timestamp"]
            waiting_time_material_output_list.append(end_time - start_time)

        return waiting_time_material_output_list

    def get_mean_duration(self, durations: list[int]) -> float:
        """Input: durations
        :return arithmetic mean of the durations (e.g., processing time, input wait time, output wait time)"""
        if not durations:
            return 0.0
        mean = sum(durations) / len(durations)
        return mean

    def get_variance_duration(self, durations: list[int]) -> float:
        """Input: durations
        :return variance of the durations (e.g., processing time, input wait time, output wait time)"""
        if not durations:
            return 0.0
        mean = sum(durations) / len(durations)
        variance = sum((x - mean) ** 2 for x in durations) / len(durations)
        return variance

    def get_std_dev_duration(self, durations: list[int]) -> float:
        """Input: durations
        :return standard deviation of the durations (e.g., processing time, input wait time, output wait time)"""
        variance = self.get_variance_duration(durations)
        std_dev = variance ** 0.5
        return std_dev

    def plot_mean_processing_times_per_machine(self):
        df = pd.DataFrame(self.machine_statistics_data)

        for machine in df["machine"].unique():
            subset = df[df["machine"] == machine]

            labels = subset["product"].tolist()
            x = np.arange(len(labels))  # x-Achse = Produktgruppen

            width = 0.25  # Balkenbreite

            fig, ax = plt.subplots(figsize=(19, 11))

            ax.bar(x - width, subset["mean_processing_time"], width, label='Processing')
            ax.bar(x, subset["mean_waiting_input_time"], width, label='Waiting for Input')
            ax.bar(x + width, subset["mean_waiting_output_time"], width, label='Waiting for Output')

            ax.set_title(f'Mean Times for Machine {machine}')
            ax.set_xlabel('Product Group')
            ax.set_ylabel('Time [SimPy units]')
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.legend()
            ax.grid(True, linestyle="--", alpha=0.5)
            plt.tight_layout()
            plt.show()

    def save_machine_statistics_table(self, filename: str = "machine_statistics_clean.csv"):
        os.makedirs(MACHINE_STATISTICS, exist_ok=True)
        filepath = os.path.join(MACHINE_STATISTICS, filename)

        cleaned_data = []

        # Gehe durch die gesammelten Daten
        for entry in self.machine_statistics_data:
            machine = entry["machine"]
            product = entry["product"]

            # Verteile die Metriken in verschiedene Spalten
            cleaned_data.append({
                "machine_id": machine,
                "product": product,
                "processing_time_mean": entry["mean_processing_time"],
                "processing_time_std_dev": entry["std_dev_processing_time"],
                "processing_time_variance": entry["variance_processing_time"],
                "waiting_input_mean": entry["mean_waiting_input_time"],
                "waiting_input_std_dev": entry["std_dev_waiting_input_time"],
                "waiting_input_variance": entry["variance_waiting_input_time"],
                "waiting_output_mean": entry["mean_waiting_output_time"],
                "waiting_output_std_dev": entry["std_dev_waiting_output_time"],
                "waiting_output_variance": entry["variance_waiting_output_time"]
            })

        # Erstelle den DataFrame mit den gesammelten Daten
        df = pd.DataFrame(cleaned_data)

        # Speichern der Tabelle im CSV-Format
        df.to_csv(filepath, index=False)

        print(f"Machine statistics table saved as {filepath}")
