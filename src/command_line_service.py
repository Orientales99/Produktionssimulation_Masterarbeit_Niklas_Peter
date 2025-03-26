from src.production.production_visualisation import ProductionVisualisation
from src.production.production import Production
from src.simulation_environmnent.simulation_environment import SimulationEnvironment


class CommandLineService:
    simulation_environment = SimulationEnvironment()
    production = Production(simulation_environment)
    production_visualisation = ProductionVisualisation(production)


    def create_production(self):
        self.production.create_production()
        self.production.set_entities()

    def start_simulation(self):
        simulation_duration = self.production.service_starting_conditions.set_simulation_duration_per_day()
        self.simulation_environment.initialise_simulation_start()
        self.simulation_environment.run_simulation(until=50)


    def visualise_layout(self):
        self.production_visualisation.visualize_layout()

