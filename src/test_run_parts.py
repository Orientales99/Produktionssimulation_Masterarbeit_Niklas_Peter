import numpy as np
import matplotlib.pyplot as plt

# RGB-Farben definieren (0-255 Skala)
white_rgb = [255, 255, 255]  # Weiß
red_rgb = [255, 0, 0]        # Rot

# Grid-Größe
grid_size = (10, 10, 3)  # 3D-Array für RGB-Farben
colors = np.full(grid_size, white_rgb, dtype=np.uint8)  # Startet mit weißen Zellen

# Setze gerade Felder auf rot
for row in range(grid_size[0]):
    for col in range(grid_size[1]):
        if row % 2 == 0 or col % 2 == 0:
            colors[row, col] = red_rgb

fig, ax = plt.subplots()
mesh = ax.imshow(colors)

# Klick-Event zum Ändern der Farben
def on_click(event):
    if event.xdata is not None and event.ydata is not None:
        col = int(event.xdata)
        row = int(event.ydata)
        current_color = colors[row, col].tolist()
        colors[row, col] = white_rgb if current_color == red_rgb else red_rgb  # Farbe umschalten
        print('Hallo')
        mesh.set_data(colors)
        plt.draw()

fig.canvas.mpl_connect('button_press_event', on_click)
plt.show()
