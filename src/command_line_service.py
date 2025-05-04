from src.production.production import Production
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.simulation_environmnent.simulation_environment import SimulationEnvironment


class CommandLineService:
    simulation_environment = SimulationEnvironment()

    service_starting_conditions = StartingConditionsService()
    production = Production(simulation_environment, service_starting_conditions)


    def start_simulation(self):
        simulation_duration = self.production.service_starting_conditions.set_simulation_duration_per_day()
        self.simulation_environment.initialise_simulation_start()
        self.simulation_environment.run_simulation(until=34000)


