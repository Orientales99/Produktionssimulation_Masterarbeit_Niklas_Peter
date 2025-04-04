import simpy

from src.process_logic.machine_execution import MachineExecution
from src.process_logic.path_finding import PathFinding
from src.process_logic.transport_robot_manager import TransportRobotManager
from src.process_logic.working_robot_manager import WorkingRobotManager
from src.production.production import Production
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.production.visualisation.production_visualisation import ProductionVisualisation


class SimulationEnvironment:
    def __init__(self):
        self.env = simpy.Environment()
        self.production = Production(self.env)
        self.manufacturing_plan = ManufacturingPlan(self.production)
        self.path_finding = PathFinding(self.production)
        self.working_robot_manager = WorkingRobotManager(self.manufacturing_plan, self.path_finding)
        self.visualize_production = ProductionVisualisation(self.production)
        self.transport_robot_manager = TransportRobotManager(self.env, self.manufacturing_plan, self.path_finding)
        self.machine_execution = MachineExecution(self.manufacturing_plan)

        # starting processes
        self.env.process(self.visualize_layout())
        self.env.process(self.wr_driving_through_production())
        self.env.process(self.tr_calculate_path())
        self.env.process(self.tr_pick_up_process())
        self.env.process(self.tr_unload_process())
        self.env.process(self.tr_driving_through_production())

    def run_simulation(self, until: int):
        self.env.run(until=until)

    def test(self):
        while True:
            print(f"Aktuelle Simulationszeit: {self.env.now}")
            yield self.env.timeout(100)

    def initialise_simulation_start(self):
        self.production.create_production()
        start_date = self.production.service_starting_conditions.set_starting_date_of_simulation()
        self.manufacturing_plan.set_parameter_for_start_of_a_simulation_day(start_date)
        self.transport_robot_manager.start_transport_robot_manager(start_date)
        self.working_robot_manager.start_working_robot_manager()

    def wr_driving_through_production(self):
        driving_speed = self.working_robot_manager.get_driving_speed_per_cell()
        while True:
            self.working_robot_manager.wr_drive_through_production()
            yield self.env.timeout(1 / driving_speed)

    def tr_calculate_path(self):
        while True:
            self.transport_robot_manager.path_calculation_for_every_requesting_tr()
            yield self.env.timeout(1)

    def tr_pick_up_process(self):
        while True:
            self.transport_robot_manager.pick_up_material_on_tr()
            yield self.env.timeout(1)

    def tr_unload_process(self):
        while True:
            self.transport_robot_manager.unload_material_from_tr()
            yield self.env.timeout(1)

    def tr_driving_through_production(self):
        driving_speed = self.transport_robot_manager.get_driving_speed_per_cell()
        while True:
            self.transport_robot_manager.tr_drive_through_production_to_pick_up_destination()
            self.transport_robot_manager.tr_drive_through_production_to_unload_destination()
            #self.visualize_production.visualize_layout()
            yield self.env.timeout(1 / driving_speed)

    def visualize_layout(self):
        driving_speed = self.transport_robot_manager.get_driving_speed_per_cell()
        while True:
            started = self.visualize_production.visualize_layout()
            if started == False:
                pass
            yield self.env.timeout(1/driving_speed)

