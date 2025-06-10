from src.production.production import Production
from src.provide_input_data.order_service import OrderService
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.simulation_environmnent.rebuilding_environment_simulation import RebuildingEnvironmentSimulation


class RebuildingCommandLineService:

    def __init__(self, control_time: int):
        self.order_service = OrderService()
        self.rebuilding_environment_simulation = RebuildingEnvironmentSimulation(self.order_service, control_time)
        self.service_starting_conditions = StartingConditionsService()
        self.production = Production(self.rebuilding_environment_simulation, self.service_starting_conditions)

    def start_simulation(self):
        simulation_duration = self.production.service_starting_conditions.set_simulation_duration_per_day()
        self.rebuilding_environment_simulation.initialise_simulation_start()
        self.rebuilding_environment_simulation.run_simulation(until=200000)
