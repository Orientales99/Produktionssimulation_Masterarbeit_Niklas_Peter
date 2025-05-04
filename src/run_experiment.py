import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

k_list = [0.6, 6]
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

for row, iterations in enumerate([0, 50]):  # Erste Zeile: Startzustand, zweite Zeile: finaler Zustand
    for col, k in enumerate(k_list):
        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (2, 4)])

        # Zufälliges Layout mit fester Seed für Reproduzierbarkeit (optional)
        pos = nx.spring_layout(G, k=k, iterations=iterations, seed=42)

        ax = axes[row][col]
        if iterations == 0:
            ax.set_title(f"Initiale Positionen (k={k})")
        else:
            ax.set_title(f"Spring Layout nach 50 Iterationen (k={k})")

        # Zeichne Knoten + Kanten
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', ax=ax)

        # Koordinatenwerte neben den Knoten
        for node, (x, y) in pos.items():
            ax.text(x, y + 0.08, f"({x:.2f}, {y:.2f})", fontsize=8, ha='center', color='darkblue')

        # Achsenformatierung
        ax.set_xlim([-2, 2])
        ax.set_ylim([-2, 2])
        ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
        ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
        ax.grid(True, linestyle=':', linewidth=0.5)

        # Achsenticks anzeigen
        ticks = np.arange(-2, 2.5, 0.5)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xlabel("X-Koordinate")
        ax.set_ylabel("Y-Koordinate")

plt.tight_layout()
plt.show()
