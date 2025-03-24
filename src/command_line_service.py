from src.production.production_visualisation import ProductionVisualisation
from src.production.production import Production


class CommandLineService:
    production = Production()
    production_visualisation = ProductionVisualisation(production)

    def create_production(self):
        self.production.create_production()
        self.production.set_entities()

    def visualise_layout(self):
        self.production_visualisation.visualize_layout()

