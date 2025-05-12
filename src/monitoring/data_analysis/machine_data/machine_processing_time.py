import glob
import os
from datetime import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from openpyxl import load_workbook
from openpyxl.worksheet.table import TableStyleInfo, Table

from src import MACHINE_STATISTICS, MACHINE_STATISTICS_GRAPH


class MachineProcessingTime:
    every_machine_during_simulation_data: dict[str, list[dict]]
    machine_identification_str_list: list[str]
    machine_statistics_per_product_data: pd.DataFrame
    total_machine_statistics_data: pd.DataFrame

    def __init__(self, creating_machine_during_simulation_dict):
        self.creating_machine_during_simulation_dict = creating_machine_during_simulation_dict

        self.every_machine_during_simulation_data = self.creating_machine_during_simulation_dict.every_machine_during_simulation_data
        self.machine_identification_str_list = self.creating_machine_during_simulation_dict.every_machine_identification_str_list

        self.machine_statistics_per_product_data = pd.DataFrame()
        self.total_machine_statistics_data = pd.DataFrame()

        self.clear_machine_statistics_files()

        self.get_production_machine_data()

        self.plot_mean_stddev_variance()
        self.save_machine_statistics_table()

    def get_production_machine_data(self):
        machine_stats_per_product_list = []
        total_machine_stats_list = []

        for identification_str in self.machine_identification_str_list:
            machine_dict_list = self.every_machine_during_simulation_data.get(identification_str)

            unique_product_list = self.get_list_of_produced_product_group_for_machine(machine_dict_list)

            machine_total_processing_time_list = []
            machine_total_waiting_input_time_list = []
            machine_total_waiting_output_time_list = []

            for product in unique_product_list:
                # analysing machine stats per product
                processing_time_per_product_list = self.get_list_processing_time_per_product(machine_dict_list, product)
                waiting_time_for_material_input_list = self.get_list_waiting_time_machine_input_empty(machine_dict_list,
                                                                                                      product)
                waiting_time_for_material_output_list = self.get_list_waiting_time_machine_output_full(
                    machine_dict_list, product)

                # add the machine stats to one big list. Cannot just add them because than list[list[int]] and
                # not list[int]

                for processing_time in processing_time_per_product_list:
                    machine_total_processing_time_list.append(processing_time)

                for waiting_input_time in waiting_time_for_material_input_list:
                    machine_total_waiting_input_time_list.append(waiting_input_time)

                for waiting_output_time in waiting_time_for_material_output_list:
                    machine_total_waiting_output_time_list.append(waiting_output_time)

                # put the machine stats per product in a list
                machine_stats_per_product_list.append({
                    "machine": identification_str,
                    "product": product,
                    "number_of_produced_product": len(processing_time_per_product_list),

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

            # get total stats for one machine
            total_machine_stats_list.append({
                "machine": identification_str,
                "number_of_produced_product": len(machine_total_processing_time_list),

                "mean_processing_time": self.get_mean_duration(machine_total_processing_time_list),
                "std_dev_processing_time": self.get_std_dev_duration(machine_total_processing_time_list),
                "variance_processing_time": self.get_variance_duration(machine_total_processing_time_list),

                "mean_waiting_input_time": self.get_mean_duration(machine_total_waiting_input_time_list),
                "std_dev_waiting_input_time": self.get_std_dev_duration(machine_total_waiting_input_time_list),
                "variance_waiting_input_time": self.get_variance_duration(machine_total_waiting_input_time_list),

                "mean_waiting_output_time": self.get_mean_duration(machine_total_waiting_output_time_list),
                "std_dev_waiting_output_time": self.get_std_dev_duration(machine_total_waiting_output_time_list),
                "variance_waiting_output_time": self.get_variance_duration(machine_total_waiting_output_time_list),
            })

        # Umwandlung in ein DataFrame
        self.machine_statistics_per_product_data = pd.DataFrame(machine_stats_per_product_list)
        self.total_machine_statistics_data = pd.DataFrame(total_machine_stats_list)

    def get_list_of_produced_product_group_for_machine(self, machine_data_during_simulation: list[dict]) -> list[str]:
        """
        Input a list of dictionaries of one machine with every status change and timestamp. Creating a list of every
        product this machine has produced in the production
        :return list of str (product group: ex. "ProductGroup.THREE.1)"""
        unique_products = set()

        for machine_dict in machine_data_during_simulation:
            for entity in machine_dict.get("entities", []):
                if entity["entity_type"] == "Machine":
                    material = entity["entity_data"]["working_status"]["producing_production_material"]
                    if material:
                        unique_products.add(material)

        return list(unique_products)

    def get_list_processing_time_per_product(self, machine_data_during_simulation: list[dict], product_group: str) -> \
            list[int]:
        """ Calculates processing durations for a specific product group based on machine status data over time.
        :return: A list of processing durations in time units."""

        processing_times = []
        is_processing = False
        start_time = None

        for machine in machine_data_during_simulation:
            timestamp = machine["timestamp"]
            for entity in machine["entities"]:

                status = entity["entity_data"]["working_status"]
                current_material = status["producing_production_material"]
                producing_item = status["producing_item"]

                conditions_met = (
                        current_material == product_group and
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

    def get_list_waiting_time_machine_input_empty(self, machine_data_during_simulation: list[dict],
                                                  product_group: str) -> list[int]:
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

    def get_list_waiting_time_machine_output_full(self, machine_data_during_simulation: list[dict],
                                                  product_group: str) -> list[int]:
        """ Calculates waiting for material output durations for a specific product group based on machine status data
            over time.
                :return: A list of waiting time ."""

        waiting_time_material_output_list = []
        is_processing = False
        start_time = None

        for entry in machine_data_during_simulation:
            timestamp = entry["timestamp"]
            for entity in entry["entities"]:

                status = entity["entity_data"]["working_status"]
                current_material = status["producing_production_material"]
                storage_status = status["storage_status"]

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

    def plot_mean_stddev_variance(self):
        # Extract machines and necessary columns from the DataFrame
        machines = self.total_machine_statistics_data["machine"]
        bar_width = 0.25
        index = np.arange(len(self.total_machine_statistics_data))

        # Create the 'Mean, Std Dev, and Variance' for Processing Time
        self._plot_time_stats(machines, index, 'processing_time', 'Processing Time', 'Processing Time', 0)

        # Create the 'Mean, Std Dev, and Variance' for Waiting Input Time
        self._plot_time_stats(machines, index, 'waiting_input_time', 'Waiting Input Time', 'Input', 1)

        # Create the 'Mean, Std Dev, and Variance' for Waiting Output Time
        self._plot_time_stats(machines, index, 'waiting_output_time', 'Waiting Output Time', 'Output', 2)

    def _plot_time_stats(self, machines, index, time_type, time_title, label_suffix, shift):
        """
        Create a bar chart for the given time statistics (mean, std dev, variance).
        :param machines: List of machine identifiers
        :param index: X-axis position of the bars
        :param time_type: Time type (processing_time, waiting_input_time, waiting_output_time)
        :param time_title: Title for the time stats chart (e.g., 'Processing Time')
        :param label_suffix: Label suffix to be used in the plot (e.g., 'Processing Time', 'Input', 'Output')
        :param shift: The shift for the x-axis to avoid overlapping bars
        """
        # Prepare figure for the bar chart
        plt.figure(figsize=(12, 6))

        # Adjust the index for plotting
        bar_positions = index + shift * 0.4  # Calculate the new X-axis positions for the bars

        # Plot Mean, Std Dev, and Variance for the current time type
        mean_bars = plt.bar(bar_positions, self.total_machine_statistics_data[f"mean_{time_type}"], 0.25,
                            label=f"Mean {time_title}", color=(113 / 255, 28 / 255, 55 / 255))
        std_dev_bars = plt.bar(bar_positions + 0.25, self.total_machine_statistics_data[f"std_dev_{time_type}"], 0.25,
                               label=f"Std Dev {time_title}", color=(161 / 255, 204 / 255, 201 / 255))
        if time_type == "processing_time":
            variance_bars = plt.bar(bar_positions + 0.5, self.total_machine_statistics_data[f"variance_{time_type}"], 0.25,
                                    label=f"Variance {time_title}", color=(219 / 255, 203 / 255, 150 / 255))
            self._add_values_on_bars(variance_bars)

        # Add the value labels on top of each bar
        self._add_values_on_bars(mean_bars)
        self._add_values_on_bars(std_dev_bars)

        # Customize the plot
        plt.xlabel('Machines')
        plt.ylabel('Time (Seconds)')
        plt.title(f'Mean, Std Dev, and Variance of {time_title}')
        plt.xticks(bar_positions + 0.25, machines, rotation=90)  # Align X-ticks with the center of the bars
        plt.legend()
        plt.tight_layout()

        # Save the plot (this will overwrite the file if it already exists)
        file_path = os.path.join(MACHINE_STATISTICS_GRAPH, f"{time_type}_stats.png")
        plt.savefig(file_path)  # No need for overwrite=True, it will automatically overwrite if the file exists
        plt.close()

    def _add_values_on_bars(self, bars):
        """
        Add values on top of each bar in a bar chart.
        :param bars: The bars object returned by plt.bar()
        """
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2),
                     ha='center', va='bottom', rotation=90, fontsize=9)

    def save_machine_statistics_table(self, filename: str = "Machine_data.xlsx"):
        # Check if MACHINE_STATISTICS directory exists, otherwise create it
        os.makedirs(MACHINE_STATISTICS, exist_ok=True)
        filepath = os.path.join(MACHINE_STATISTICS, filename)

        # Step 1: Save both DataFrames to an Excel file with different sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Save the two DataFrames in their respective sheets
            self.machine_statistics_per_product_data.to_excel(writer, index=False,
                                                              sheet_name='Machine Stats Per Product')
            self.total_machine_statistics_data.to_excel(writer, index=False, sheet_name='Total Machine Stats')

        # Step 2: Load the Excel file using openpyxl
        workbook = load_workbook(filepath)

        # Step 3: Skip table formatting (removed _apply_table_formatting)

        # Step 4: Save the Excel file without additional formatting
        workbook.save(filepath)

    def _apply_table_formatting(self, worksheet):
        # Generiere einen eindeutigen Tabellennamen, z. B. mit einem Zeitstempel
        unique_table_name = "MachineStatsTable_" + datetime.now().strftime("%Y%m%d%H%M%S")

        # Erstelle die Tabelle mit dem einzigartigen Namen
        max_row = worksheet.max_row
        max_col = worksheet.max_column
        last_col_letter = worksheet.cell(row=1, column=max_col).column_letter
        table_range = f"A1:{last_col_letter}{max_row}"

        # Erstelle die Tabelle
        table = Table(displayName=unique_table_name, ref=table_range)

        # Formatieren der Tabelle
        style = TableStyleInfo(
            name="TableStyleMedium9",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False
        )
        table.tableStyleInfo = style
        worksheet.add_table(table)

    def clear_machine_statistics_files(self):
        # Define the paths to the directories
        machine_statistics_dir = MACHINE_STATISTICS
        machine_statistics_graph_dir = MACHINE_STATISTICS_GRAPH

        # Delete all .xlsx files in MACHINE_STATISTICS directory
        xlsx_files = glob.glob(os.path.join(machine_statistics_dir, "*.xlsx"))
        for file in xlsx_files:
            try:
                os.remove(file)
                print(f"Deleted {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")

        # Delete all .png files in MACHINE_STATISTICS_GRAPH directory
        png_files = glob.glob(os.path.join(machine_statistics_graph_dir, "*.png"))
        for file in png_files:
            try:
                os.remove(file)
                print(f"Deleted {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")