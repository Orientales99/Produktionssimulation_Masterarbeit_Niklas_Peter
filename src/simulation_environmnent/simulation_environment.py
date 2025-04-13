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
        self.machine_execution = MachineExecution(self.env, self.manufacturing_plan, self.machine_manager)
        self.working_robot_manager = WorkingRobotManager(self.manufacturing_plan, self.path_finding)
        self.visualize_production = ProductionVisualisation(self.production, self.env)
        self.transport_robot_manager = TransportRobotManager(self.env, self.manufacturing_plan, self.path_finding,
                                                             self.machine_execution, self.machine_manager)

        self.stop_event = False

        # starting processes
        self.env.process(self.visualize_layout())
        self.env.process(self.wr_driving_through_production())
        self.env.process(self.tr_process())


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
        self.working_robot_manager.start_working_robot_manager()
        self.run_machine_process()

    def wr_driving_through_production(self):
        driving_speed = self.working_robot_manager.get_driving_speed_per_cell()
        while True:
            if self.stop_event is False:
                self.working_robot_manager.wr_drive_through_production()
            yield self.env.timeout(1 / driving_speed)

    def tr_process(self):
        self.tr_list = self.transport_robot_manager.tr_list
        self.tr_rdy_to_get_new_order_list = self.transport_robot_manager.list_tr_rdy_to_get_new_order
        self.tr_drive_to_pick_up_list = self.transport_robot_manager.list_tr_drive_to_pick_up
        self.arrived_tr_on_pick_up_destination_list = self.transport_robot_manager.list_arrived_tr_on_pick_up_destination
        self.loaded_tr_drive_to_unload_list = self.transport_robot_manager.list_loaded_tr_drive_to_unload
        self.arrived_tr_on_unload_destination_list = self.transport_robot_manager.list_arrived_tr_on_unload_destination

        while True:
            if self.stop_event is False:
                for tr in self.tr_list:

                    # tr get new order
                    if tr in self.tr_rdy_to_get_new_order_list:
                        self.transport_robot_manager.get_transport_request_list()
                        self.transport_robot_manager.get_transport_order_list()
                        if self.transport_robot_manager.get_transport_order_for_tr(tr) is True:
                            tr.working_status.waiting_for_order = False
                            if self.transport_robot_manager.get_path_for_tr_pick_up(tr) is True:
                                self.tr_rdy_to_get_new_order_list.remove(tr)
                                self.tr_drive_to_pick_up_list.append(tr)

                                tr.working_status.driving_to_new_location = True

                    # tr drives to pick up station
                    if tr in self.tr_drive_to_pick_up_list:
                        self.tr_drive_to_pick_up_list.remove(tr)
                        self.env.process(self.tr_driving_through_production_to_pick_up(tr))

                    # tr picks up material
                    if tr in self.arrived_tr_on_pick_up_destination_list:
                        self.arrived_tr_on_pick_up_destination_list.remove(tr)
                        self.env.process(self.tr_pick_up_process(tr))

                    # tr drives to unload station
                    if tr in self.loaded_tr_drive_to_unload_list:
                        self.loaded_tr_drive_to_unload_list.remove(tr)
                        self.env.process(self.tr_driving_through_production_to_unload(tr))

                    # tr unloads material
                    if tr in self.arrived_tr_on_unload_destination_list:
                        self.arrived_tr_on_unload_destination_list.remove(tr)
                        self.env.process(self.tr_unload_process(tr))

            self.transport_robot_manager.get_all_lists()
            yield self.env.timeout(1)

    def tr_driving_through_production_to_pick_up(self, tr: TransportRobot):
        driving_speed = self.transport_robot_manager.get_driving_speed_per_cell()
        while True:
            if self.stop_event is False:
                if self.transport_robot_manager.tr_drive_through_production_to_pick_up_destination(tr) is True:
                    break
            yield self.env.timeout(1 / driving_speed)

        self.arrived_tr_on_pick_up_destination_list.append(tr)
        tr.working_status.driving_to_new_location = False

    def tr_driving_through_production_to_unload(self, tr: TransportRobot):
        driving_speed = self.transport_robot_manager.get_driving_speed_per_cell()

        if tr.working_status.driving_route_unload_material is None:
            while True:
                if self.transport_robot_manager.get_path_for_tr_unload(tr):
                    break
                yield self.env.timeout(2)

        while True:
            if self.stop_event is False:

                if self.transport_robot_manager.tr_drive_through_production_to_unload_destination(tr) is True:
                    break
            yield self.env.timeout(1 / driving_speed)

        self.arrived_tr_on_unload_destination_list.append(tr)
        tr.working_status.driving_to_new_location = False

    def tr_pick_up_process(self, tr: TransportRobot):
        loading_speed = self.transport_robot_manager.get_loading_speed()

        if self.transport_robot_manager.pick_up_material_on_tr(tr) is True:
            yield self.env.timeout(loading_speed)

            self.loaded_tr_drive_to_unload_list.append(tr)
            self.transport_robot_manager.get_path_for_tr_unload(tr)

            tr.working_status.driving_to_new_location = True

    def tr_unload_process(self, tr: TransportRobot):
        loading_speed = self.transport_robot_manager.get_loading_speed()
        arrived_tr: list[TransportRobot]
        if self.transport_robot_manager.unload_single_tr(tr) is True:
            yield self.env.timeout(loading_speed)

            tr.working_status.waiting_for_order = True
            tr.transport_order = None
            self.tr_rdy_to_get_new_order_list.append(tr)

    def run_machine_process(self):
        for machine in self.production.machine_list:
            self.env.process(self.machine_execution.run_machine_production(machine))

    def visualize_layout(self):
        driving_speed = self.transport_robot_manager.get_driving_speed_per_cell()
        while True:
            stop_event = self.visualize_production.visualize_layout()
            if stop_event is False:
                self.stop_event = False
            if stop_event is True:
                self.stop_event = True
            yield self.env.timeout(1 / driving_speed)
