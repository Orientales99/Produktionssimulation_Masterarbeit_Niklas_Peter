import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from src import ANALYSIS_SOLUTION


class MaterialFlowHeatmap:
    def __init__(self, material_flow_matrix: dict[str, dict[str, int]]):
        self.material_flow_matrix = material_flow_matrix
        self.df_matrix = self.convert_to_dataframe()

    def convert_to_dataframe(self, station_order: list[str] = None) -> pd.DataFrame:
        """
        Wandelt das verschachtelte Dictionary in ein Pandas DataFrame um.
        Zeilen: von Stationen
        Spalten: zu Stationen
        Werte: Transportierte Menge
        """
        df = pd.DataFrame(self.material_flow_matrix).fillna(0).astype(int)

        if station_order:
            # Reihenfolge für Zeilen und Spalten festlegen (Stationsnamen, die nicht in station_order sind, fallen weg)
            df = df.reindex(index=station_order, columns=station_order, fill_value=0)
        else:
            df = df.sort_index(axis=0).sort_index(axis=1)
        return df

    def get_custom_cmap(self):
        """
        Erstellt eine Farbpalette, die bei niedrigen Werten sehr hell ist und
        bei hohen Werten dunkel wird, basierend auf rgb(116,33,40).
        """
        base_color = (116 / 255, 33 / 255, 40 / 255)
        # reverse=True macht die hellste Farbe bei kleinsten Werten
        return sns.light_palette(base_color, as_cmap=True, reverse=False)

    def plot(self, figsize: tuple[int, int] = (10, 8),
             annot: bool = True, fmt: str = "d", title: str = "Materialfluss Heatmap"):
        if self.df_matrix.empty:
            print("Warnung: Die Materialflussmatrix ist leer. Keine Heatmap wird erzeugt.")
            return

        ANALYSIS_SOLUTION.mkdir(parents=True, exist_ok=True)
        save_path = ANALYSIS_SOLUTION / "Heatmap_Materialfluss.png"

        custom_cmap = self.get_custom_cmap()

        plt.figure(figsize=figsize)
        sns.heatmap(
            self.df_matrix,
            annot=annot,
            fmt=fmt,
            cmap=custom_cmap,
            linewidths=0.5,
            linecolor='gray'
        )
        plt.title(title)
        plt.xlabel("Quellstation")
        plt.ylabel("Zielstation")
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
