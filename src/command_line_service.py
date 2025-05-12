from src.production.production import Production
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.simulation_environmnent.environment_simulation import EnvironmentSimulation


class CommandLineService:
    environment_simulation = EnvironmentSimulation()

    service_starting_conditions = StartingConditionsService()
    production = Production(environment_simulation, service_starting_conditions)

    def start_simulation(self):
        simulation_duration = self.production.service_starting_conditions.set_simulation_duration_per_day()
        self.environment_simulation.initialise_simulation_start()
        self.environment_simulation.run_simulation(until=28799)


