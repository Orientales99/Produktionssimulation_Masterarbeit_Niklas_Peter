import json
import os
import shutil

from matplotlib import colors

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
        """Generates a plot for each product group and also saves the data as JSON."""
        all_product_groups = pd.concat([
            self.convert_json_data.goods_receipt_production_df["Product Group"],
            self.convert_json_data.finished_products_leaving_production_df["Product Group"]
        ]).unique()

        all_data = {}
        for product_group in all_product_groups:
            df = self.prepare_data(product_group)
            all_data[product_group] = df
            self.plot_goods_receipt_over_time(product_group)

        # Gesamtdaten auch in JSON integrieren
        df_total = self.prepare_total_data()
        all_data["Total"] = df_total

        self.plot_total_cumulative_line()
        self.save_plot_data_as_json(all_data)


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

        ax.set_title(f'Kumulierte Menge für Produkt: {product_group}')
        ax.set_xlabel('Zeit (dd:mm:ss)')
        ax.set_ylabel('Kumulierte Menge')
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

        filename = f"Produkt {product_group} - Produktionsbestand.png"
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
        # hours = seconds // 3600
        # minutes = (seconds % 3600) // 60
        # secs = seconds % 60
        # return f"{hours:02}:{minutes:02}:{secs:02}"

        hours = (seconds % 28800) // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"Time: {hours:02d}:{minutes:02d}:{seconds:02d} \n"

    def plot_all_product_groups_with_legend(self) -> None:
        INTERVAL = 28800  # 8 Stunden in Sekunden

        all_product_groups = pd.concat([
            self.convert_json_data.goods_receipt_production_df["Product Group"],
            self.convert_json_data.finished_products_leaving_production_df["Product Group"]
        ]).unique()

        # Maximaler Zeitpunkt über alle Produktgruppen bestimmen
        max_time_overall = 0
        for product_group in all_product_groups:
            df_combined = self.prepare_data(product_group)
            max_time = df_combined["Time"].max()
            if max_time > max_time_overall:
                max_time_overall = max_time
        # Auch für Gesamtdaten
        df_total = self.prepare_total_data()
        if df_total["Time"].max() > max_time_overall:
            max_time_overall = df_total["Time"].max()

        # Anzahl der Tage/Intervalle ermitteln (1-basierte Anzahl)
        num_intervals = int(max_time_overall // INTERVAL) + 1

        colors = plt.cm.get_cmap('tab20', len(all_product_groups))

        for interval_idx in range(num_intervals):
            upper_limit = (interval_idx + 1) * INTERVAL
            lower_limit = interval_idx * INTERVAL

            fig, ax = plt.subplots(figsize=(19, 11))

            tick_positions = []
            tick_labels = []

            interval_data_exists = False
            interval_min_time = upper_limit
            interval_max_time = lower_limit

            for idx, product_group in enumerate(all_product_groups):
                df_combined = self.prepare_data(product_group)
                df_interval = df_combined[(df_combined["Time"] >= lower_limit) & (df_combined["Time"] <= upper_limit)]

                if df_interval.empty:
                    continue

                interval_data_exists = True
                interval_min_time = min(interval_min_time, df_interval["Time"].min())
                interval_max_time = max(interval_max_time, df_interval["Time"].max())

                color = colors(idx)
                self.plot_lines(ax, df_interval, color=color, label=product_group, with_markers=False)

            # Gesamtdatenlinie im Intervall
            df_total_interval = df_total[(df_total["Time"] >= lower_limit) & (df_total["Time"] <= upper_limit)]
            if not df_total_interval.empty:
                interval_data_exists = True
                interval_min_time = min(interval_min_time, df_total_interval["Time"].min())
                interval_max_time = max(interval_max_time, df_total_interval["Time"].max())
                self.plot_lines(ax, df_total_interval, color="black", label="Total Cumulative", with_markers=False)



            if not interval_data_exists:
                plt.close(fig)
                continue  # Skip empty plot

            # Ticks innerhalb des effektiven Zeitbereichs erzeugen
            tick_positions = self.generate_time_ticks(interval_max_time)
            tick_positions = [t for t in tick_positions if interval_min_time <= t <= interval_max_time]
            tick_labels = [self.seconds_to_hours_minutes_seconds(t) for t in tick_positions]

            ax.set_xlim(interval_min_time, interval_max_time)  # Nur aktiver Bereich auf X-Achse
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45)
            ax.set_title(f'Alle Produktgruppen - Produktionsbestandskurve (Tag {interval_idx + 1})')
            ax.set_xlabel('Zeit (hh:mm:ss)')
            ax.set_ylabel('Kumulierte Menge')
            ax.grid(True)
            ax.legend(title="Product Groups", bbox_to_anchor=(-0.15, 1), loc='upper left')

            self.save_plot(fig, GRAPH_PRODUCTION_MATERIAL,
                           f"Alle Produktgruppen - Produktionsbestandskurve {interval_idx + 1}.png")

            plt.close(fig)


    def plot_lines(self, ax, df_combined: pd.DataFrame, color: str, label: str, with_markers: bool = True) -> None:
        previous_time = 0
        previous_cumulative_quantity = 0
        label_added = False

        for i, row in df_combined.iterrows():
            current_time = row["Time"]
            current_cumulative_quantity = row["Cumulative Quantity"]

            marker = 'o' if with_markers else None

            if isinstance(current_time, pd.Series):
                current_time = current_time.iloc[0]
            if isinstance(previous_time, pd.Series):
                previous_time = previous_time.iloc[0]

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
        """Creates a separate graph for all products together."""
        df_total = self.prepare_total_data()

        max_time = df_total["Time"].max()
        tick_positions = self.generate_time_ticks(max_time)
        tick_labels = [self.seconds_to_hours_minutes_seconds(t) for t in tick_positions]

        fig, ax = plt.subplots(figsize=(19, 11))
        self.plot_lines(ax, df_total, color="black", label="Total Cumulative", )

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45)
        ax.set_title('Alle Produktgruppen Kumulierte Menge - Produktionsbestandskurve')
        ax.set_xlabel('Zeit (dd:mm:ss)')
        ax.set_ylabel('Kumulierte Menge')
        ax.grid(True)
        ax.legend()

        self.save_plot(fig, GRAPH_PRODUCTION_MATERIAL, "Cumulative Quantity - Production inventory curve.png")

    def prepare_total_data(self) -> pd.DataFrame:
        df_in = self.convert_json_data.goods_receipt_production_df.copy()
        df_out = self.convert_json_data.finished_products_leaving_production_df.copy()

        df_in = df_in[["Time", "Quantity"]]
        df_in["Quantity Change"] = df_in["Quantity"]

        df_out = df_out[["Time", "Quantity"]]
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


    def save_plot_data_as_json(self, all_data: dict) -> None:
        """Saves the history of cumulative quantities per product group as a JSON file."""
        os.makedirs(GRAPH_PRODUCTION_MATERIAL, exist_ok=True)
        json_path = os.path.join(GRAPH_PRODUCTION_MATERIAL, "production_throughput_data.json")

        clean_data = {
            group: [{"time": int(d["Time"]), "cumulative_quantity": int(d["Cumulative Quantity"])}
                    for d in data.to_dict(orient="records")]
            for group, data in all_data.items()
        }

        with open(json_path, "w") as f:
            json.dump(clean_data, f, indent=4)
        print(f"JSON-Daten gespeichert unter: {json_path}")


