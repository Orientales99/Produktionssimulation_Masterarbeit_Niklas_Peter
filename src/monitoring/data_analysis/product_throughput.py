import json
import numpy as np
import pandas as pd
from typing import Dict
from datetime import timedelta
from src import ANALYSIS_SOLUTION


class ProductThroughput:
    def __init__(self, convert_json_data):
        self.convert_json_data = convert_json_data
        self.entry_products_df = self.convert_json_data.get_df_goods_entering_production()
        self.exit_products_df = self.convert_json_data.get_df_finished_products_leaving_production()

    def filter_and_sort_by_product_group(self, df: pd.DataFrame, product_group: str) -> pd.DataFrame:
        """Filters the DataFrame by product group and sorts by time."""
        df_filtered = df[df["Product Group"] == product_group].copy()
        return df_filtered.sort_values("Time")

    def build_entry_queue(self, entry_df: pd.DataFrame) -> list[list[int, int]]:
        """Builds a FIFO queue from the entry DataFrame."""
        return [[row["Quantity"], row["Time"]] for _, row in entry_df.iterrows()]

    def process_exit_row(self, exit_quantity: int, exit_time: int, entry_queue: list[list[int]]) -> \
            tuple[int, int, list[int]]:
        """Processes a single exit row using FIFO logic."""
        total_time = 0
        total_quantity = 0
        remaining_qty = exit_quantity
        individual_times = []

        while remaining_qty > 0 and entry_queue:
            entry_qty, entry_time = entry_queue[0]
            qty_to_process = min(entry_qty, remaining_qty)

            time_diff = exit_time - entry_time
            total_time += qty_to_process * time_diff
            total_quantity += qty_to_process
            individual_times.extend([time_diff] * qty_to_process)

            entry_queue[0][0] -= qty_to_process
            if entry_queue[0][0] == 0:
                entry_queue.pop(0)

            remaining_qty -= qty_to_process

        return total_time, total_quantity, individual_times

    def convert_seconds_to_hours_minutes_seconds(self, seconds: float) -> str:
        """Converts seconds to a time string in the format HH:MM:SS"""
        seconds = int(seconds)  # Ensure seconds is an integer
        time_obj = timedelta(seconds=seconds)
        return str(time_obj)

    def calculate_throughput_stats_fifo(self, product_group: str) -> Dict[str, str]:
        """
        Calculates average and standard deviation of throughput times (FIFO-based) for a given product group
        :return Dictionary with average and std deviation in HH:MM:SS format.
        """
        entry_sorted = self.filter_and_sort_by_product_group(self.entry_products_df, product_group)
        exit_sorted = self.filter_and_sort_by_product_group(self.exit_products_df, product_group)
        entry_queue = self.build_entry_queue(entry_sorted)

        all_times = []
        for _, exit_row in exit_sorted.iterrows():
            _, _, times = self.process_exit_row(exit_row["Quantity"], exit_row["Time"], entry_queue)
            all_times.extend(times)

        if not all_times:
            return {
                "average": "00:00:00",
                "std_dev": "00:00:00"
            }

        # Calculate the average and standard deviation in seconds
        average_seconds = np.mean(all_times)
        std_dev_seconds = np.std(all_times)

        # Convert to HH:MM:SS format
        average_time = self.convert_seconds_to_hours_minutes_seconds(average_seconds)
        std_dev_time = self.convert_seconds_to_hours_minutes_seconds(std_dev_seconds)

        return {
            "average": average_time,
            "std_dev": std_dev_time
        }

    def calculate_throughput_for_all_groups(self):
        """Calculates average FIFO throughput time and standard deviation for all product groups."""
        all_groups = pd.concat([
            self.entry_products_df["Product Group"],
            self.exit_products_df["Product Group"]
        ]).unique()

        throughput_stats_all_groups = {}
        all_individual_times = []

        for group in all_groups:
            stats = self.calculate_throughput_stats_fifo(group)
            throughput_stats_all_groups[group] = stats

            # Collect individual times for total average/std if available
            entry_sorted = self.filter_and_sort_by_product_group(self.entry_products_df, group)
            exit_sorted = self.filter_and_sort_by_product_group(self.exit_products_df, group)
            entry_queue = self.build_entry_queue(entry_sorted)

            for _, exit_row in exit_sorted.iterrows():
                _, _, times = self.process_exit_row(exit_row["Quantity"], exit_row["Time"], entry_queue)
                all_individual_times.extend(times)

        # Save as JSON
        save_path = ANALYSIS_SOLUTION / "throughput_all_products.json"
        with open(save_path, "w") as f:
            json.dump(throughput_stats_all_groups, f, indent=4)

