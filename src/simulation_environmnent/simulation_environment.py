import simpy

from src.constant.constant import TransportRobotStatus, WorkingRobotStatus, MachineProcessStatus, \
    MachineWorkingRobotStatus, MachineStorageStatus
from src.entity.machine.machine import Machine
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot
from src.process_logic.machine.machine_execution import MachineExecution
from src.process_logic.machine.machine_manager import Machine_Manager
from src.process_logic.path_finding import PathFinding
from src.process_logic.transport_robot.tr_executing_order import TrExecutingOrder
from src.process_logic.transport_robot.tr_order_manager import TrOrderManager
from src.process_logic.working_robot_order_manager import WorkingRobotOrderManager
from src.production.production import Production
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.production.store_manager import StoreManager
from src.production.visualisation.production_visualisation import ProductionVisualisation
from src.provide_input_data.starting_condition_service import StartingConditionsService


class SimulationEnvironment:
    def __init__(self):
        self.env = simpy.Environment()
        self.service_starting_conditions = StartingConditionsService()
        self.production = Production(self.env, self.service_starting_conditions)
        self.store_manager = StoreManager(self.env)
        self.path_finding = PathFinding(self.production)

        self.machine_manager = Machine_Manager(self.production, self.store_manager)
        self.manufacturing_plan = ManufacturingPlan(self.production, self.machine_manager)
        self.machine_execution = MachineExecution(self.env, self.manufacturing_plan, self.machine_manager,
                                                  self.store_manager)
        self.working_robot_manager = WorkingRobotOrderManager(self.manufacturing_plan, self.path_finding)
        # self.visualize_production = ProductionVisualisation(self.production, self.env)
        self.tr_order_manager = TrOrderManager(self.env, self.manufacturing_plan, self.machine_manager,
                                               self.store_manager)
        self.tr_executing_order = TrExecutingOrder(self.env, self.manufacturing_plan, self.path_finding,
                                                   self.machine_execution, self.machine_manager, self.store_manager)

        self.stop_event = False

        # starting processes
        # self.env.process(self.visualize_layout())
        self.env.process(self.print_simulation_time())
        self.env.process(self.start_every_wr_process())
        self.env.process(self.start_every_tr_process())
        self.env.process(self.run_machine_process())

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

    ###################################################################################################################

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

                    # wr drives to waiting location
                    if wr.working_status.status == WorkingRobotStatus.IDLE and \
                            wr.working_status.working_on_status is False and \
                            self.working_robot_manager.check_if_tr_is_on_waiting_place(wr) is False:
                        wr.working_status.status = WorkingRobotStatus.RETURNING
                        wr.working_status.working_on_status = True
                        self.env.process(self.drive_wr_to_destination_process(wr))

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

                yield self.env.timeout(1)
            else:
                yield self.env.timeout(1)

    def wr_get_working_order(self, wr: WorkingRobot):
        if self.stop_event is False:
            if self.working_robot_manager.get_next_working_location_for_order(wr) is True:

                while True:
                    print(f"{wr.identification_str}")
                    if self.working_robot_manager.get_path_for_wr(wr) is True:
                        wr.working_status.status = WorkingRobotStatus.MOVING_TO_MACHINE
                        wr.working_status.working_on_status = False
                        break
                    yield self.env.timeout(3)
            yield self.env.timeout(1)

    def drive_wr_to_destination_process(self, wr: WorkingRobot):
        driving_speed = self.working_robot_manager.get_driving_speed_per_cell()

        while True:
            if self.stop_event is False:
                driving_bool = self.working_robot_manager.drive_wr_one_step_trough_production(wr)
                if driving_bool is True:
                    if wr.working_status.status == WorkingRobotStatus.MOVING_TO_MACHINE:
                        wr.working_status.status = WorkingRobotStatus.WAITING_IN_FRONT_OF_MACHINE
                        wr.working_status.working_on_status = False
                        break

                    elif wr.working_status.status == WorkingRobotStatus.RETURNING:
                        wr.working_status.status = WorkingRobotStatus.IDLE
                        wr.working_status.working_on_status = False
                        break

                elif driving_bool is Exception:
                    yield self.env.timeout(2)

            yield self.env.timeout(1 / driving_speed)

        yield self.env.timeout(1)

    def wr_exit_machine_process(self, wr: WorkingRobot):
        while True:
            wr_is_off_machine = self.working_robot_manager.wr_driving_off_machine(wr)
            if wr_is_off_machine is True:
                print(f"{wr.identification_str} drives off the machine")
                wr.working_status.working_for_machine.working_status.working_robot_status = \
                    MachineWorkingRobotStatus.NO_WR

                wr.working_status.working_for_machine = None
                wr.working_status.driving_destination_coordinates = None
                wr.working_status.driving_route = None
                wr.working_status.last_placement_in_production = None

                wr.working_status.status = WorkingRobotStatus.IDLE
                wr.working_status.working_on_status = False
                break

            yield self.env.timeout(2)

    ###############################################################################################################

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
                        else:
                            tr.working_status.working_on_status = False

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
                        else:
                            tr.working_status.working_on_status = False

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
                yield self.env.timeout(1 / driving_speed)
                driving_value = self.tr_executing_order.drive_tr_one_step_trough_production(tr)
                if driving_value is True:

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

                elif driving_value is Exception:
                    yield self.env.timeout(4)

    def pick_up_material_on_tr_process(self, tr: TransportRobot):
        loading_speed = self.tr_order_manager.get_loading_speed()
        yield self.env.timeout(loading_speed)
        if self.tr_executing_order.pick_up_material_on_tr(tr):

            tr.working_status.status = TransportRobotStatus.MOVING_TO_DROP_OFF
            tr.working_status.working_on_status = False
            if isinstance(tr.transport_order.pick_up_station, Machine):
                tr.transport_order.pick_up_station.working_status.waiting_for_arriving_of_tr = False
                tr.transport_order.pick_up_station.working_status.storage_status = \
                    MachineStorageStatus.STORAGES_READY_FOR_PRODUCTION

    def unload_material_off_tr_process(self, tr: TransportRobot):
        loading_speed = self.tr_order_manager.get_loading_speed()
        yield self.env.timeout(loading_speed)
        if self.tr_executing_order.unload_material_off_tr(tr):

            tr.working_status.status = TransportRobotStatus.IDLE
            tr.working_status.working_on_status = False
            if isinstance(tr.transport_order.unload_destination, Machine):
                tr.transport_order.unload_destination.working_status.waiting_for_arriving_of_tr = False

    ###################################################################################################################

    def run_machine_process(self):
        while True:
            if self.stop_event is False:
                for machine in self.production.machine_list:

                    # set machine process status: idle
                    if len(machine.processing_list) == 0:
                        machine.working_status.process_status = MachineProcessStatus.IDLE

                    # set machine process status: waiting next order
                    if len(machine.processing_list) != 0 and \
                            machine.working_status.process_status == MachineProcessStatus.IDLE:
                        machine.working_status.process_status = MachineProcessStatus.WAITING_NEXT_ORDER

                    # wr is present -> setu up machine
                    if machine.working_status.working_robot_status == MachineWorkingRobotStatus.WR_PRESENT and \
                            machine.working_status.process_status == MachineProcessStatus.WAITING_NEXT_ORDER and \
                            machine.working_status.working_on_status is False:
                        machine.working_status.working_on_status = True
                        self.set_up_machine_process(machine)

                    if machine.working_status.process_status == MachineProcessStatus.READY_TO_PRODUCE and \
                            machine.working_status.working_on_status is False:
                        machine.working_status.working_on_status = True
                        self.env.process(self.producing_process(machine))

                    #   producing product
                    #       get order for the next machine in the process steps of the product
                    #       if output full -> wait (other than producing product)
                    #       if input empty -> wait
                    #   producing product finished
                    #       -> release wr; machine status -> wr_leaving -> no wr
                    #       machine status -> idle or waiting_next_order

            yield self.env.timeout(1)

    def set_up_machine_process(self, machine: Machine):
        producing_item = machine.process_material_list[0].producing_material

        # set up machine if necessary
        if machine.working_status.producing_production_material is None \
                or producing_item.production_material_id != \
                machine.working_status.producing_production_material.production_material_id:

            machine.working_status.process_status = MachineProcessStatus.SETUP

            self.env.process(self.machine_execution.start__set_up_machine__process(machine, producing_item))

        elif producing_item.production_material_id == \
                machine.working_status.producing_production_material.production_material_id:
            machine.working_status.process_status = MachineProcessStatus.READY_TO_PRODUCE
            machine.working_status.working_on_status = False

    def producing_process(self, machine: Machine):
        required_material = machine.process_material_list[0].required_material
        producing_material = machine.process_material_list[0].producing_material

        # get a new order for the next producing step of the machine
        self.machine_execution.give_order_to_next_machine(producing_material, machine)

        while True:
            if self.stop_event is False:
                # check if space is in output_store
                if self.store_manager.count_empty_space_in_store(machine.machine_storage.storage_after_process) == 0 \
                        or self.store_manager.check_no_other_material_is_in_store(
                    machine.machine_storage.storage_after_process, producing_material) is False and \
                        machine.working_status.process_status != MachineProcessStatus.FINISHED_TO_PRODUCE:
                    machine.working_status.process_status = MachineProcessStatus.PRODUCING_PAUSED
                    machine.working_status.storage_status = MachineStorageStatus.OUTPUT_FULL
                    yield self.env.timeout(1)

                # check if material is in input_store
                elif self.machine_manager.check_required_material_in_storage_before_process(machine,
                                                                                        required_material) is False \
                        and machine.working_status.process_status != MachineProcessStatus.FINISHED_TO_PRODUCE:
                    machine.working_status.process_status = MachineProcessStatus.PRODUCING_PAUSED
                    machine.working_status.storage_status = MachineStorageStatus.INPUT_EMPTY
                    yield self.env.timeout(1)
                elif machine.working_status.process_status != MachineProcessStatus.FINISHED_TO_PRODUCE:
                    machine.working_status.process_status = MachineProcessStatus.READY_TO_PRODUCE
                    machine.working_status.storage_status = MachineStorageStatus.STORAGES_READY_FOR_PRODUCTION

                # start producing process und einen begriff für den Process in
                if machine.working_status.process_status == MachineProcessStatus.READY_TO_PRODUCE and \
                        machine.working_status.working_robot_status == MachineWorkingRobotStatus.WR_PRESENT:
                    machine.working_status.process_status = MachineProcessStatus.PRODUCING_PRODUCT

                    self.env.process(self.machine_execution.produce_one_item(machine, required_material,
                                                                             producing_material))

                if machine.working_status.process_status == MachineProcessStatus.FINISHED_TO_PRODUCE:
                    machine.working_status.working_on_status = False
                    if len(machine.processing_list) == 0:
                        machine.working_status.process_status = MachineProcessStatus.IDLE
                    else:
                        machine.working_status.process_status = MachineProcessStatus.WAITING_NEXT_ORDER
                    break
            yield self.env.timeout(1)

    ###################################################################################################################

    def visualize_layout(self):
        driving_speed = self.tr_order_manager.get_driving_speed_per_cell()
        while True:
            stop_event = self.visualize_production.visualize_layout()
            if stop_event is False:
                self.stop_event = False
            if stop_event is True:
                self.stop_event = True
            yield self.env.timeout(1 / driving_speed)

    def print_simulation_time(self):
        """Printing the current simulation time in h:min:sec."""
        while True:
            sim_time = int(self.env.now)  # Simulationszeit in Sekunden
            hours = sim_time // 3600
            minutes = (sim_time % 3600) // 60
            seconds = sim_time % 60
            print(f"Simulationszeit: {hours:02d}:{minutes:02d}:{seconds:02d}")
            yield self.env.timeout(10)
