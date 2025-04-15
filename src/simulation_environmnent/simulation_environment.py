import simpy

from src.constant.constant import TransportRobotStatus, WorkingRobotStatus
from src.entity.machine.machine import Machine
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot
from src.process_logic.machine.machine_execution import MachineExecution
from src.process_logic.machine.machine_manager import Machine_Manager
from src.process_logic.path_finding import PathFinding
from src.process_logic.transport_robot.tr_executing_order import TrExecutingOrder
from src.process_logic.transport_robot.tr_order_manager import TrOrderManager
from src.process_logic.working_robot_order_manager import WorkingRobotManager
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
        self.tr_order_manager = TrOrderManager(self.env, self.manufacturing_plan, self.machine_manager)
        self.tr_executing_order = TrExecutingOrder(self.env, self.manufacturing_plan, self.path_finding,
                                                   self.machine_execution, self.machine_manager)

        self.stop_event = False

        # starting processes
        self.env.process(self.visualize_layout())
        self.env.process(self.start_every_wr_process())
        self.env.process(self.start_every_tr_process())

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
        self.run_machine_process()

    def start_every_wr_process(self):
        while True:
            if self.stop_event is False:
                self.working_robot_manager.sort_process_order_list_for_wr()

                for wr in self.working_robot_manager.wr_list:

                    # get new working order
                    if wr.working_status.status == WorkingRobotStatus.IDLE and \
                            wr.working_status.working_on_status is False:
                        wr.working_status.working_on_status = True
                        self.env.process(self.wr_get_working_order(wr))

                    # drive to destination
                    if wr.working_status.status == WorkingRobotStatus.MOVING_TO_MACHINE and \
                            wr.working_status.working_on_status is False:
                        wr.working_status.working_on_status = True

                        self.env.process(self.drive_wr_to_destination_process(wr))

                    # wr drives on the machine
                    if wr.working_status.status == WorkingRobotStatus.WAITING_IN_FRONT_OF_MACHINE and \
                            wr.working_status.working_on_status is False:
                        wr.working_status.working_on_status = True
                        self.working_robot_manager.wr_driving_in_machine(wr)
                        wr.working_status.status = WorkingRobotStatus.WORKING_ON_MACHINE

                    # working process on the machine happens in the class machine_execution

                    # wr drives off the machine
                    if wr.working_status.status == WorkingRobotStatus.WAITING_IN_MACHINE_TO_EXIT and \
                            wr.working_status.working_on_status is False:
                        self.env.process(self.wr_exit_machine_process(wr))


                    # wr drives to waiting location
                    if wr.working_status.status == WorkingRobotStatus.IDLE and \
                            wr.working_status.working_on_status is False:
                        print(f"Has to drive Home: {wr.identification_str}")
                        if self.working_robot_manager.check_if_tr_is_on_waiting_place(wr) is False:
                            wr.working_status.status = WorkingRobotStatus.RETURNING
                            wr.working_status.working_on_status = True

                            self.env.process(self.drive_wr_to_destination_process(wr))



            yield self.env.timeout(5)

    def wr_get_working_order(self, wr: WorkingRobot):
        if self.stop_event is False:
            if self.working_robot_manager.get_next_working_location_for_order(wr):

                while True:
                    if self.working_robot_manager.get_path_for_wr(wr):
                        wr.working_status.status = WorkingRobotStatus.MOVING_TO_MACHINE
                        wr.working_status.working_on_status = False
                        break
                    else:
                        yield self.env.timeout(3)

    def drive_wr_to_destination_process(self, wr: WorkingRobot):
        driving_speed = self.working_robot_manager.get_driving_speed_per_cell()

        while True:
            if self.stop_event is False:
                if self.working_robot_manager.drive_wr_one_step_trough_production(wr) is True:
                    if wr.working_status.status == WorkingRobotStatus.MOVING_TO_MACHINE:
                        wr.working_status.status = WorkingRobotStatus.WAITING_IN_FRONT_OF_MACHINE
                        wr.working_status.working_on_status = False
                        break
                    elif wr.working_status.status == WorkingRobotStatus.RETURNING:
                        wr.working_status.status = WorkingRobotStatus.IDLE
                        wr.working_status.working_on_status = False
                        break

            yield self.env.timeout(1 / driving_speed)

    def wr_exit_machine_process(self, wr: WorkingRobot):
        while True:
            if self.working_robot_manager.wr_driving_off_machine(wr):

                wr.working_status.working_for_machine = None
                wr.working_status.driving_destination_coordinates = None
                wr.working_status.driving_route = None
                wr.working_status.last_placement_in_production = None

                wr.working_status.status = WorkingRobotStatus.IDLE
                wr.working_status.working_on_status = False
                break

            yield self.env.timeout(2)

    def start_every_tr_process(self):
        while True:
            if self.stop_event is False:

                self.tr_order_manager.create_transport_request_list_from_machines()
                self.tr_order_manager.every_idle_tr_get_order()

                for tr in self.tr_order_manager.tr_list:

                    # drive to pick up destination
                    if tr.working_status.status == TransportRobotStatus.MOVING_TO_PICKUP \
                            and tr.working_status.working_on_status is False:

                        tr.working_status.working_on_status = True
                        if self.tr_executing_order.start__moving_to_pick_up__process_for_tr(tr):
                            self.env.process(self.tr_drive_to_destination_process(tr))

                    # pick up material
                    if tr.working_status.status == TransportRobotStatus.LOADING \
                            and tr.working_status.working_on_status is False:
                        tr.working_status.working_on_status = True
                        self.env.process(self.pick_up_material_on_tr_process(tr))

                    # drive to unload destination
                    if tr.working_status.status == TransportRobotStatus.MOVING_TO_DROP_OFF \
                            and tr.working_status.working_on_status is False:

                        tr.working_status.working_on_status = True
                        if self.tr_executing_order.start__moving_to_unload__process_for_tr(tr):
                            self.env.process(self.tr_drive_to_destination_process(tr))

                    # unload material
                    if tr.working_status.status == TransportRobotStatus.UNLOADING \
                            and tr.working_status.working_on_status is False:
                        tr.working_status.working_on_status = True
                        self.env.process(self.unload_material_off_tr_process(tr))

                    # drive to waiting position
                    if tr.working_status.status == TransportRobotStatus.IDLE \
                            and tr.working_status.working_on_status is False:
                        if self.tr_executing_order.check_if_tr_is_on_waiting_place(tr) is False:
                            tr.working_status.status = TransportRobotStatus.RETURNING
                            tr.working_status.working_on_status = True
                            if self.tr_executing_order.start__moving_to_waiting__process_for_tr(tr):
                                self.env.process(self.tr_drive_to_destination_process(tr))
            yield self.env.timeout(1)

    def tr_drive_to_destination_process(self, tr: TransportRobot):
        driving_speed = self.tr_order_manager.get_driving_speed_per_cell()

        while True:
            if self.stop_event is False:
                if self.tr_executing_order.drive_tr_one_step_trough_production(tr) is True:

                    if tr.working_status.status == TransportRobotStatus.MOVING_TO_PICKUP:
                        tr.working_status.status = TransportRobotStatus.LOADING
                        tr.working_status.working_on_status = False
                        break

                    elif tr.working_status.status == TransportRobotStatus.MOVING_TO_DROP_OFF:
                        tr.working_status.status = TransportRobotStatus.UNLOADING
                        tr.working_status.working_on_status = False
                        break

                    elif tr.working_status.status == TransportRobotStatus.RETURNING:
                        tr.working_status.status = TransportRobotStatus.IDLE
                        tr.working_status.working_on_status = False
                        break

                    else:
                        raise Exception(
                            f"{tr.identification_str} drives to destination but has wrong working_status.status: "
                            f"{tr.working_status.status}")

            yield self.env.timeout(1 / driving_speed)

    def pick_up_material_on_tr_process(self, tr: TransportRobot):
        loading_speed = self.tr_order_manager.get_loading_speed()
        yield self.env.timeout(loading_speed)
        if self.tr_executing_order.pick_up_material_on_tr(tr):

            tr.working_status.status = TransportRobotStatus.MOVING_TO_DROP_OFF
            tr.working_status.working_on_status = False
            if isinstance(tr.transport_order.pick_up_station, Machine):
                tr.transport_order.pick_up_station.waiting_for_arriving_of_tr = False

    def unload_material_off_tr_process(self, tr: TransportRobot):
        loading_speed = self.tr_order_manager.get_loading_speed()
        yield self.env.timeout(loading_speed)
        if self.tr_executing_order.unload_material_off_tr(tr):

            tr.working_status.status = TransportRobotStatus.IDLE
            tr.working_status.working_on_status = False
            if isinstance(tr.transport_order.unload_destination, Machine):
                tr.transport_order.unload_destination.waiting_for_arriving_of_tr = False

    def run_machine_process(self):
        for machine in self.production.machine_list:
            self.env.process(self.machine_execution.run_machine_production(machine))

    def visualize_layout(self):
        driving_speed = self.tr_order_manager.get_driving_speed_per_cell()
        while True:
            stop_event = self.visualize_production.visualize_layout()
            if stop_event is False:
                self.stop_event = False
            if stop_event is True:
                self.stop_event = True
            yield self.env.timeout(1 / driving_speed)
