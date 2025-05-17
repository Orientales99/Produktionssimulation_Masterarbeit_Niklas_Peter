import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

k_list = [0.6, 6]
iteration_steps = [0, 5, 50000]
fig, axes = plt.subplots(len(iteration_steps), len(k_list), figsize=(12, 18))

for row, iterations in enumerate(iteration_steps):
    for col, k in enumerate(k_list):
        G = nx.Graph()
        # Ursprüngliche Kanten
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (2, 4)])
        # Neue Knoten + Verbindungen
        G.add_edges_from([(1, 5), (3, 6), (4, 7), (5, 6), (6, 7)])

        # Layout berechnen
        pos = nx.spring_layout(G, k=k, iterations=iterations, seed=10)

        ax = axes[row][col]
        if iterations == 0:
            ax.set_title(f"Initiale Positionen (k={k})")
        elif iterations == 5:
            ax.set_title(f"Spring Layout nach 5 Iterationen (k={k})")
        else:
            ax.set_title(f"Spring Layout nach 500 Iterationen (k={k})")

        # Zeichne Knoten + Kanten
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', ax=ax)

        # Koordinaten anzeigen
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

plt.subplots_adjust(top=5)
plt.tight_layout()
plt.show()
