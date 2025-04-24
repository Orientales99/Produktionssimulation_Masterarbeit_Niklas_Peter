import os

from src.monitoring.data_analysis.convert_json_data import ConvertJsonData
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src import GRAPH_PRODUCTION_MATERIAL


class VisualizeProductionMaterialThroughput:
    convert_json_data: ConvertJsonData

    def __init__(self, convert_json_data):
        self.convert_json_data = convert_json_data

    def plot_and_save_for_all_product_groups(self) -> None:
        """Get all unique product groups from the DataFrames (df_1 and df_2)"""
        all_product_groups = pd.concat([
            self.convert_json_data.goods_receipt_production_df["Product Group"],
            self.convert_json_data.finished_products_leaving_production_df["Product Group"]
        ]).unique()

        for product_group in all_product_groups:
            self.plot_goods_receipt_over_time(product_group)

        self.plot_total_cumulative_line()

    def prepare_data(self, product_group: str) -> pd.DataFrame:
        # Prepare incoming goods data
        df_in = self.get_filtered_cumulative_df(
            self.convert_json_data.goods_receipt_production_df, product_group)
        df_in = df_in[["Time", "Quantity"]].copy()
        df_in["Quantity Change"] = df_in["Quantity"]

        # Prepare outgoing goods data
        df_out = self.get_filtered_cumulative_df(
            self.convert_json_data.finished_products_leaving_production_df, product_group)
        df_out = df_out[["Time", "Quantity"]].copy()
        df_out["Quantity Change"] = -df_out["Quantity"]

        # Combine both dataframes
        df_combined = pd.concat([df_in, df_out], ignore_index=True)
        df_combined = df_combined.sort_values("Time")

        # Compute cumulative quantity
        df_combined["Cumulative Quantity"] = df_combined["Quantity Change"].cumsum()

        # Add (0, 0) point if it does not yet exist
        if not (df_combined["Time"].iloc[0] == 0 and df_combined["Cumulative Quantity"].iloc[0] == 0):
            df_combined = pd.concat([
                pd.DataFrame([[0, 0, 0, 0]], columns=["Time", "Quantity", "Quantity Change", "Cumulative Quantity"]),
                df_combined
            ], ignore_index=True)

        return df_combined

    def plot_goods_receipt_over_time(self, product_group: str) -> None:
        df_combined = self.prepare_data(product_group)

        max_time = df_combined["Time"].max()
        tick_positions = self.generate_time_ticks(max_time)
        tick_labels = [self.seconds_to_hours_minutes_seconds(t) for t in tick_positions]

        # Plot setup
        fig, ax = plt.subplots(figsize=(19, 11))

        # Plot the lines
        self.plot_lines(ax, df_combined, color=(113 / 255, 28 / 255, 55 / 255), label=product_group)

        ax.set_xticks(list(tick_positions))
        ax.set_xticklabels(tick_labels, rotation=45)

        ax.set_title(f'Cumulative Quantity over Time for Product Group: {product_group}')
        ax.set_xlabel('Time (hh:mm:ss)')
        ax.set_ylabel('Cumulative Quantity')
        ax.grid(True)

        # Annotate each point
        for i, row in df_combined.iterrows():
            time_str = self.seconds_to_hours_minutes_seconds(row["Time"])
            quantity = row["Cumulative Quantity"]
            ax.annotate(f'Time: {time_str}\nQuantity: {quantity}',
                        (row["Time"], quantity),
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha='center', fontsize=8)

        filename = f"Product {product_group} - Production inventory curve.png"
        self.save_plot(fig, GRAPH_PRODUCTION_MATERIAL, filename)

    def save_plot(self, fig, directory: str, filename: str) -> None:
        """Saves a matplotlib-figure object in the specified directory."""

        os.makedirs(directory, exist_ok=True)
        save_path = os.path.join(directory, filename)
        fig.savefig(save_path)
        print(f"Graph saved to: {save_path}")

    def get_filtered_cumulative_df(self, df: pd.DataFrame, product_group: str) -> pd.DataFrame:
        filtered_df = df[df["Product Group"] == product_group].copy()
        filtered_df = filtered_df.sort_values("Time")
        filtered_df["Cumulative Quantity"] = filtered_df["Quantity"].cumsum()
        return filtered_df

    def generate_time_ticks(self, max_time: int, step: int = 600) -> list:
        """:return a generate list of time steps"""
        return list(np.arange(0, max_time + 1, step))

    def seconds_to_hours_minutes_seconds(self, seconds: int) -> str:
        """:return a str with 00:00:00; h:min:sec"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02}:{minutes:02}:{secs:02}"

    def plot_all_product_groups_with_legend(self) -> None:
        all_product_groups = pd.concat([
            self.convert_json_data.goods_receipt_production_df["Product Group"],
            self.convert_json_data.finished_products_leaving_production_df["Product Group"]
        ]).unique()

        fig, ax = plt.subplots(figsize=(19, 11))
        colors = plt.cm.get_cmap('tab20', len(all_product_groups))

        tick_positions = []
        tick_labels = []

        for idx, product_group in enumerate(all_product_groups):
            df_combined = self.prepare_data(product_group)

            max_time = df_combined["Time"].max()
            group_tick_positions = self.generate_time_ticks(max_time)
            tick_positions.extend(group_tick_positions)
            tick_labels.extend([self.seconds_to_hours_minutes_seconds(t) for t in group_tick_positions])

            color = colors(idx)
            self.plot_lines(ax, df_combined, color=color, label=product_group, with_markers=False)

        # Gesamtdatenlinie hinzufügen
        df_total = self.prepare_total_data()
        self.plot_lines(ax, df_total, color="black", label="Total Cumulative", with_markers=False)

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45)
        ax.set_title('All Product Groups - Production inventory curve')
        ax.set_xlabel('Time (hh:mm:ss)')
        ax.set_ylabel('Cumulative Quantity')
        ax.grid(True)
        ax.legend(title="Product Groups", bbox_to_anchor=(-0.15, 1), loc='upper left')

        self.save_plot(fig, GRAPH_PRODUCTION_MATERIAL, "All Product Groups - Production inventory curve.png")

    def plot_lines(self, ax, df_combined: pd.DataFrame, color: str, label: str, with_markers: bool = True) -> None:
        previous_time = 0
        previous_cumulative_quantity = 0
        label_added = False

        for i, row in df_combined.iterrows():
            current_time = row["Time"]
            current_cumulative_quantity = row["Cumulative Quantity"]

            marker = 'o' if with_markers else None

            if current_time > previous_time:
                ax.plot([previous_time, current_time],
                        [previous_cumulative_quantity, previous_cumulative_quantity],
                        color=color, linestyle='-', marker=marker, label=label if not label_added else "")
                label_added = True

            if current_cumulative_quantity != previous_cumulative_quantity:
                ax.plot([current_time, current_time],
                        [previous_cumulative_quantity, current_cumulative_quantity],
                        color=color, linestyle='-', marker=marker, label=label if not label_added else "")
                label_added = True

            previous_time = current_time
            previous_cumulative_quantity = current_cumulative_quantity

    def plot_total_cumulative_line(self) -> None:
        """Erzeugt einen separaten Graphen für alle Produkte zusammen."""
        df_total = self.prepare_total_data()

        max_time = df_total["Time"].max()
        tick_positions = self.generate_time_ticks(max_time)
        tick_labels = [self.seconds_to_hours_minutes_seconds(t) for t in tick_positions]

        fig, ax = plt.subplots(figsize=(19, 11))
        self.plot_lines(ax, df_total, color="black", label="Total Cumulative", )

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45)
        ax.set_title('All Product Groups Cumulative Quantity - Production inventory curve ')
        ax.set_xlabel('Time (hh:mm:ss)')
        ax.set_ylabel('Cumulative Quantity')
        ax.grid(True)
        ax.legend()

        self.save_plot(fig, GRAPH_PRODUCTION_MATERIAL, "Cumulative Quantity - Production inventory curve.png")

    def prepare_total_data(self) -> pd.DataFrame:
        """Berechnet die kumulierte Menge aller Produkte über die Zeit"""
        df_in = self.convert_json_data.goods_receipt_production_df.copy()
        df_in["Quantity Change"] = df_in["Quantity"]

        df_out = self.convert_json_data.finished_products_leaving_production_df.copy()
        df_out["Quantity Change"] = -df_out["Quantity"]

        df_combined = pd.concat([df_in, df_out], ignore_index=True)
        df_combined = df_combined.sort_values("Time")
        df_combined["Cumulative Quantity"] = df_combined["Quantity Change"].cumsum()

        if not (df_combined["Time"].iloc[0] == 0 and df_combined["Cumulative Quantity"].iloc[0] == 0):
            df_combined = pd.concat([
                pd.DataFrame([[0, 0, 0, 0]], columns=["Time", "Quantity", "Quantity Change", "Cumulative Quantity"]),
                df_combined
            ], ignore_index=True)

        return df_combined
