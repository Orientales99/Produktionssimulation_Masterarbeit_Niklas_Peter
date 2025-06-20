import pygame
import simpy

from src.entity.intermediate_store import IntermediateStore
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.production.production import Production
from src.constant.constant import ColorRGB, WorkingRobotStatus, MachineWorkingRobotStatus
from src.production.visualisation.cell_information import CellInformation
from src.simulation_environmnent.simulation_control import SimulationControl


class PygameVisualisation:
    production: Production
    cell_information: CellInformation
    production_layout: list[list[Cell]]
    grid: list[list]
    grid_off_set: int
    start: bool

    def __init__(self, production: Production, env: simpy.Environment, simulation_control: SimulationControl):
        pygame.init()
        self.env = env
        self.production = production
        self.simulation_control = simulation_control
        self.cell_information = CellInformation(self.production)
        self.max_coordinates = self.production.service_starting_conditions.set_max_coordinates_for_production_layout()
        self.production_layout = self.production.production_layout

        self.width_x = None
        self.width_y = None
        self.window = None
        self.grid = []
        self.grid_off_set = 45
        self.start = False

        self.get_width_of_layout()
        self.set_display()
        self.caption_for_display()

    def visualize_production_layout_in_pygame(self):
        self.make_grid()
        self.draw_grid_lines()
        self.draw_everything()
        run = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # Left Mouse button
                position = pygame.mouse.get_pos()
                row, col = self.get_clicked_pos(position)

                button_pressed = self.check_button_click(position)

                if button_pressed == "start":
                    # Aktion für Start-Button, z.B. Simulation starten
                    self.simulation_control.stop_event = False

                elif button_pressed == "stop":
                    # Aktion für Stop-Button, z.B. Simulation stoppen
                    self.simulation_control.stop_event = True

                self.cell_information.run_cell_information_printed(Coordinates(row, col))
                print(f"Reihe: {row}")
                print(f"Col: {col}")

    def set_display(self):
        self.window = pygame.display.set_mode((self.width_x, self.width_y))

    def caption_for_display(self):
        pygame.display.set_caption("Production Simulation", "Masterthesis: Niklas Peter")

    def get_width_of_layout(self):
        self.width_x = self.max_coordinates.x * 9
        self.width_y = self.max_coordinates.y * 9 + self.grid_off_set

    def make_grid(self):
        self.rows = self.max_coordinates.x
        self.col = self.max_coordinates.y
        self.grid = []
        gap_x = self.width_x // self.rows
        gap_y = self.width_y // self.col
        for y, row in enumerate(self.production.production_layout):
            self.grid.append([])
            for x, cell in enumerate(row):
                spot = PygameSpot(y, x, gap_x, gap_y, self.rows, cell)
                self.grid[y].append(spot)

    def draw_grid_lines(self):
        gap_x = self.width_x // self.rows
        gap_y = self.width_y // self.col
        for index, row in enumerate(self.production.production_layout):
            pygame.draw.line(self.window, ColorRGB.DARK_GRAY.value, (0, index * gap_y + self.grid_off_set),
                             (self.width_x, index * gap_y + self.grid_off_set))
            for j in range(self.rows):
                pygame.draw.line(self.window, ColorRGB.DARK_GRAY.value, (j * gap_x, self.grid_off_set),
                                 (j * gap_x, self.width_y))

    def draw_start_stop_buttons(self):
        """Zeichnet rechteckige Buttons mit den Beschriftungen 'Start' und 'Stop'."""
        font = pygame.font.SysFont('Arial', 24)  # Verwenden einer Standard-Schriftart

        button_width = 100
        button_height = 30
        padding = 20  # Abstand zwischen den Buttons

        start_x = 10  # Position für den ersten Button von links
        start_y = 10  # Position für den ersten Button von oben

        # Start-Button (weiss mit schwarzem Rand)
        self.start_button_rect = pygame.Rect(start_x, start_y, button_width, button_height)
        pygame.draw.rect(self.window, (255, 255, 255), self.start_button_rect)  # Weiß
        pygame.draw.rect(self.window, (0, 0, 0), self.start_button_rect, 3)  # Schwarzer Rand
        start_text = font.render("Start", True, (0, 0, 0))  # Text für 'Start' in Schwarz
        self.window.blit(start_text, (start_x + (button_width - start_text.get_width()) // 2,
                                      start_y + (button_height - start_text.get_height()) // 2))

        # Stop-Button (weiss mit schwarzem Rand)
        stop_x = start_x + button_width + padding  # Position für den Stop-Button
        self.stop_button_rect = pygame.Rect(stop_x, start_y, button_width, button_height)
        pygame.draw.rect(self.window, (255, 255, 255), self.stop_button_rect)  # Weiß
        pygame.draw.rect(self.window, (0, 0, 0), self.stop_button_rect, 3)  # Schwarzer Rand
        stop_text = font.render("Stop", True, (0, 0, 0))  # Text für 'Stop' in Schwarz
        self.window.blit(stop_text, (
            stop_x + (button_width - stop_text.get_width()) // 2,
            start_y + (button_height - stop_text.get_height()) // 2))

    def draw_simulation_time(self):
        """Zeigt SimPy-Zeit als Tag, Stunde, Minute und Sekunde rechts neben den Buttons an."""
        font = pygame.font.SysFont('Arial', 20)
        sim_time = int(self.env.now)

        tage = sim_time // (8 * 3600)
        rest = sim_time % (8 * 3600)
        stunden = rest // 3600
        rest %= 3600
        minuten = rest // 60
        sekunden = rest % 60

        labels = [("Produktionstag", tage), ("Std", stunden), ("Min", minuten), ("Sek", sekunden)]

        x = self.stop_button_rect.right + 30
        y = 15
        padding = 20

        for label, value in labels:
            text = f"{label}: {value:02d}"
            text_surface = font.render(text, True, (0, 0, 0))
            self.window.blit(text_surface, (x, y))
            x += text_surface.get_width() + padding

    def draw_everything(self):
        """Zeichnet das gesamte Layout und verschiebt das Grid nach unten."""
        self.window.fill(ColorRGB.WHITE.value)
        self.draw_start_stop_buttons()
        self.draw_simulation_time()

        grid_offset_y = self.grid_off_set

        for row in self.grid:
            for spot in row:
                spot.draw(self.window, offset_y=grid_offset_y)

        self.draw_grid_lines()
        pygame.display.update()

    def get_clicked_pos(self, position):
        gap_x = self.width_x // self.rows
        gap_y = self.width_y // self.col

        y, x = position

        row = y // gap_y
        col = (self.max_coordinates.y - x // gap_x) + 4

        return row, col

    def check_button_click(self, position):
        """Überprüft, ob einer der Buttons (Start oder Stop) angeklickt wurde."""
        if self.start_button_rect.collidepoint(position):
            print("Start-Button wurde geklickt")
            return "start"

        elif self.stop_button_rect.collidepoint(position):
            print("Stop-Button wurde geklickt")
            return "stop"

        return None


class PygameSpot:

    def __init__(self, row, col, width_x, width_y, total_rows, cell):
        self.row = row
        self.col = col
        self.y = row * width_x
        self.x = col * width_y
        self.color = ColorRGB.WHITE.value
        self.width_x = width_x
        self.width_y = width_y
        self.total_rows = total_rows
        self.cell = cell
        self.get_color()

    def get_pos(self):
        return self.row, self.col

    def get_color(self):
        self.make_wr_waiting()
        self.make_wr_driving()

        self.make_tr_without_material()
        self.make_tr_transporting_material()

        self.make_machine_waiting_to_process()
        self.make_machine_processing()
        self.make_intermediate_store()

        self.make_sink()
        self.make_source()

    def is_wr_waiting(self):
        return self.color == ColorRGB.ORANGE.value

    def is_wr_driving(self):
        return self.color == ColorRGB.YELLOW.value

    def is_tr_transporting_material(self):
        return self.color == ColorRGB.DARK_GRAY.value

    def is_tr_without_material(self):
        return self.color == ColorRGB.BLACK.value

    def is_machine_waiting_to_process(self):
        return self.color == ColorRGB.RED.value

    def is_machine_processing(self):
        return self.color == ColorRGB.GREEN.value

    def is_source(self):
        return self.color == ColorRGB.BLUE.value

    def is_sink(self):
        return self.color == ColorRGB.SILVER.value

    def make_wr_waiting(self):
        if isinstance(self.cell.placed_entity, WorkingRobot):
            if self.cell.placed_entity.working_status.status == WorkingRobotStatus.IDLE:
                self.color = ColorRGB.YELLOW.value

    def make_wr_driving(self):
        if isinstance(self.cell.placed_entity, WorkingRobot):
            if self.cell.placed_entity.working_status.status != WorkingRobotStatus.IDLE:
                self.color = ColorRGB.ORANGE.value

    def make_tr_transporting_material(self):
        if isinstance(self.cell.placed_entity, TransportRobot):
            if len(self.cell.placed_entity.material_store.items) > 0:
                self.color = ColorRGB.DARK_GRAY.value

    def make_tr_without_material(self):
        if isinstance(self.cell.placed_entity, TransportRobot):
            if len(self.cell.placed_entity.material_store.items) == 0:
                self.color = ColorRGB.BLACK.value

    def make_machine_waiting_to_process(self):
        if isinstance(self.cell.placed_entity, Machine):
            if self.cell.placed_entity.working_status.working_robot_status != MachineWorkingRobotStatus.WR_PRESENT:
                self.color = ColorRGB.RED.value

    def make_machine_processing(self):
        if isinstance(self.cell.placed_entity, Machine):
            if self.cell.placed_entity.working_status.working_robot_status == MachineWorkingRobotStatus.WR_PRESENT:
                self.color = ColorRGB.GREEN.value

    def make_intermediate_store(self):
        if isinstance(self.cell.placed_entity, IntermediateStore):
            self.color = ColorRGB.PURPLE.value

    def make_source(self):
        if isinstance(self.cell.placed_entity, Source):
            self.color = ColorRGB.BLUE.value

    def make_sink(self):
        if isinstance(self.cell.placed_entity, Sink):
            self.color = ColorRGB.SILVER.value

    def draw(self, window, offset_y=0):
        pygame.draw.rect(window, self.color, (self.x, self.y + offset_y, self.width_x, self.width_y))

    def __lt__(self, other):
        return False  # lt-> less than, compare two spot objects
