from matplotlib import pyplot as plt

from src.data.coordinates import Coordinates
from src.data.production_visualisation import ProductionVisualisation
from src.data.service_order import ServiceOrder
from src.data.production import Production
from src.data.simulation_environment import SimulationEnvironment


class CommandLineService:
    production = Production()
    production_visualisation = ProductionVisualisation()

    def create_production(self):
        self.production.create_production()
        self.production.set_entities()

    def visualise_layout(self):
        self.production_visualisation.visualize_layout()

