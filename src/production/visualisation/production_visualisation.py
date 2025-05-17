import simpy

from src.production.production import Production
from src.production.visualisation.pygame_visualisation import PygameVisualisation
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.production.visualisation.terminal_visualisation import TerminalVisualisation
from src.production.visualisation.matplotlib_visualisation import MatplotlibVisualisation
from src.simulation_environmnent.simulation_control import SimulationControl


class ProductionVisualisation:
    production: Production
    service_starting_conditions = StartingConditionsService()
    matplotlib_visualisation: MatplotlibVisualisation
    terminal_visualisation: TerminalVisualisation
    pygames_visualisation: PygameVisualisation

    def __init__(self, production: Production, env: simpy.Environment, simulation_control: SimulationControl):
        self.production = production
        self.env = env
        self.simulation_control = simulation_control
        self.matplotlib_visualisation = MatplotlibVisualisation(self.production)
        self.terminal_visualisation = TerminalVisualisation(self.production)
        self.pygames_visualisation = PygameVisualisation(self.production, self.env, self.simulation_control)

    def visualize_layout(self):
        if self.service_starting_conditions.set_visualising_via_matplotlib() is True:
            self.matplotlib_visualisation.visualize_production_layout_in_matplotlib()
        if self.service_starting_conditions.set_visualising_via_terminal() is True:
            self.terminal_visualisation.visualize_production_layout_in_terminal()
        if self.service_starting_conditions.set_visualising_via_pygames() is True:
            self.pygames_visualisation.visualize_production_layout_in_pygame()



