from src.production.production import Production
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.simulation_environmnent.buck_fixing_environment_simulation import BuckFixingEnvironmentSimulation


class BuckFixingCommandLineService:
    buck_fixing_environment_simulation = BuckFixingEnvironmentSimulation()
    service_starting_conditions = StartingConditionsService()
    production = Production(buck_fixing_environment_simulation, service_starting_conditions)

    def start_simulation(self):
        simulation_duration = self.production.service_starting_conditions.set_simulation_duration_per_day()
        self.buck_fixing_environment_simulation.initialise_simulation_start()
        self.buck_fixing_environment_simulation.run_simulation(until=86400)
