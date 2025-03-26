import simpy

from src.process_logic.path_finding import PathFinding
from src.process_logic.working_robot_manager import WorkingRobotManager
from src.production.production import Production
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.production.production_visualisation import ProductionVisualisation


class SimulationEnvironment:
    def __init__(self):
        self.env = simpy.Environment()
        self.production = Production(self.env)
        self.manufacturing_plan = ManufacturingPlan(self.production)
        self.path_finding = PathFinding(self.production)
        self.working_robot_manager = WorkingRobotManager(self.manufacturing_plan, self.path_finding)
        self.visualize_production = ProductionVisualisation(self.production)

        #starting processes
        self.env.process(self.visualize_layout())
        self.env.process(self.entities_driving_through_production())


    def run_simulation(self, until: int):
        self.env.process(self.test())
        self.env.run(until=until)

    def test(self):
        while True:
            print(f"Aktuelle Simulationszeit: {self.env.now}")
            yield self.env.timeout(100)

    def initialise_simulation_start(self):
        self.production.create_production()
        start_date = self.production.service_starting_conditions.set_starting_date_of_simulation()
        self.manufacturing_plan.set_parameter_for_start_of_a_simulation_day(start_date)
        self.working_robot_manager.start_working_robot_manager()


    def entities_driving_through_production(self):
        while True:
            driving_speed = self.working_robot_manager.get_driving_speed_per_cell()
            self.working_robot_manager.wr_drive_through_production()
            yield self.env.timeout(1 / driving_speed)

    def visualize_layout(self):
        while True:
            self.visualize_production.visualize_layout()
            yield self.env.timeout(100)
