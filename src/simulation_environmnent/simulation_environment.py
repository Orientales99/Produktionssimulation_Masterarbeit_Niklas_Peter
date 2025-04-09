import simpy

from src.entity.transport_robot import TransportRobot
from src.process_logic.machine_execution import MachineExecution
from src.process_logic.machine_manager import Machine_Manager
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

        self.path_finding = PathFinding(self.production)
        self.machine_manager = Machine_Manager(self.production)
        self.manufacturing_plan = ManufacturingPlan(self.production, self.machine_manager)
        self.machine_execution = MachineExecution(self.env, self.manufacturing_plan)
        self.working_robot_manager = WorkingRobotManager(self.manufacturing_plan, self.path_finding)
        self.visualize_production = ProductionVisualisation(self.production, self.env)
        self.transport_robot_manager = TransportRobotManager(self.env, self.manufacturing_plan, self.path_finding, self.machine_manager)

        self.stop_event = False

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
        self.run_machine_process()

    def wr_driving_through_production(self):
        driving_speed = self.working_robot_manager.get_driving_speed_per_cell()
        while True:
            if self.stop_event is False:
                self.working_robot_manager.wr_drive_through_production()
            yield self.env.timeout(1 / driving_speed)

    def tr_calculate_path(self):
        while True:
            if self.stop_event is False:
                self.transport_robot_manager.path_calculation_for_every_requesting_tr()
            yield self.env.timeout(1)

    def tr_pick_up_process(self):
        loading_speed = self.transport_robot_manager.get_loading_speed()
        while True:
            if self.stop_event is False:
                arrived_tr = self.transport_robot_manager.list_arrived_tr_on_pick_up_destination[:]
                for tr in arrived_tr:
                    self.env.process(self.transport_robot_manager.pick_up_material_on_tr(tr))

                yield self.env.timeout(loading_speed)

                # After expiry → Remove robot from the list and move to next phase
                for tr in arrived_tr:
                    if tr in self.transport_robot_manager.list_arrived_tr_on_pick_up_destination:
                        self.transport_robot_manager.list_arrived_tr_on_pick_up_destination.remove(tr)
                        self.transport_robot_manager.list_loaded_tr_drive_to_unload.append(tr)
            else:
                yield self.env.timeout(loading_speed)


    def tr_unload_process(self):
        loading_speed = self.transport_robot_manager.get_loading_speed()
        arrived_tr: list[TransportRobot]
        while True:
            if self.stop_event is False:
                arrived_tr = self.transport_robot_manager.arrived_tr_on_unload_destination[:]
                unload_processes = []

                for tr in arrived_tr:
                    p = self.env.process(self.transport_robot_manager.unload_single_tr(tr))
                    unload_processes.append(p)

                yield self.env.timeout(loading_speed)

                # After expiry: Remove all TR from the arrival list and add them to the path planning
                for tr in arrived_tr:
                    if tr in self.transport_robot_manager.arrived_tr_on_unload_destination:
                        self.transport_robot_manager.arrived_tr_on_unload_destination.remove(tr)
                        self.transport_robot_manager.list_tr_rdy_to_calculate_path.append(tr)
                        tr.working_status.driving_to_new_location = True
            else:
                yield self.env.timeout(loading_speed)

    def run_machine_process(self):
        for machine in self.production.machine_list:
            self.env.process(self.machine_execution.run_machine_production(machine))


    def tr_driving_through_production(self):
        driving_speed = self.transport_robot_manager.get_driving_speed_per_cell()
        while True:
            if self.stop_event is False:
                self.transport_robot_manager.tr_drive_through_production_to_pick_up_destination()
                self.transport_robot_manager.tr_drive_through_production_to_unload_destination()

            yield self.env.timeout(1 / driving_speed)

    def visualize_layout(self):
        driving_speed = self.transport_robot_manager.get_driving_speed_per_cell()
        while True:
            stop_event = self.visualize_production.visualize_layout()
            if stop_event is False:
                self.stop_event = False
            if stop_event is True:
                self.stop_event = True
            yield self.env.timeout(1/driving_speed)


