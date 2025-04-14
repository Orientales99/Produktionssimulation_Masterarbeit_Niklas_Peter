import simpy

from src.constant.constant import TransportRobotStatus
from src.entity.transport_robot.transport_robot import TransportRobot
from src.process_logic.machine.machine_execution import MachineExecution
from src.process_logic.machine.machine_manager import Machine_Manager
from src.process_logic.path_finding import PathFinding
from src.process_logic.transport_robot.tr_executing_order import TrExecutingOrder
from src.process_logic.transport_robot.transport_robot_manager_1 import TransportRobotManager_1
from src.process_logic.transport_robot.tr_order_manager import TrOrderManager
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
        self.tr_order_manager = TrOrderManager(self.env, self.manufacturing_plan, self.machine_manager)
        self.tr_executing_order = TrExecutingOrder(self.env, self.manufacturing_plan, self.path_finding,
                                                   self.machine_execution, self.machine_manager)

        self.stop_event = False

        # starting processes
        self.env.process(self.visualize_layout())
        self.env.process(self.wr_driving_through_production())
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
        self.working_robot_manager.start_working_robot_manager()
        self.run_machine_process()

    def wr_driving_through_production(self):
        driving_speed = self.working_robot_manager.get_driving_speed_per_cell()
        while True:
            if self.stop_event is False:
                self.working_robot_manager.wr_drive_through_production()
            yield self.env.timeout(1 / driving_speed)

    def start_every_tr_process(self):
        while True:
            if self.stop_event is False:
                self.tr_order_manager.create_transport_request_list_from_machines()
                self.tr_order_manager.every_idle_tr_get_order()

                for tr in self.tr_order_manager.tr_list:

                    # drive to pick up destination
                    if tr.working_status.status == TransportRobotStatus.MOVING_TO_PICKUP:
                        if self.tr_executing_order.start__moving_to_pick_up__process_for_tr(tr):
                            self.env.process(self.tr_drive_to_destination_process(tr))

                    # pick up material
                    if tr.working_status.status == TransportRobotStatus.LOADING:
                        self.env.process(self.pick_up_material_on_tr_process(tr))

                    # drive to unload destination
                    if tr.working_status.status == TransportRobotStatus.MOVING_TO_DROP_OFF:
                        if self.tr_executing_order.start__moving_to_unload__process_for_tr(tr):
                            self.env.process(self.tr_drive_to_destination_process(tr))
                            pass
                yield self.env.timeout(20)

    def tr_drive_to_destination_process(self, tr: TransportRobot):
        driving_speed = self.tr_order_manager.get_driving_speed_per_cell()

        while True:
            if self.stop_event is False:
                if self.tr_executing_order.drive_tr_one_step_trough_production(tr) is True:
                    if tr.working_status.status == TransportRobotStatus.MOVING_TO_PICKUP:
                        tr.working_status.status = TransportRobotStatus.LOADING
                    elif tr.working_status.status == TransportRobotStatus.MOVING_TO_DROP_OFF:
                        tr.working_status.status = TransportRobotStatus.UNLOADING
                    else:
                        raise Exception(f"{tr.identification_str} drives to destination but has wrong working_status.status")
                    break
            yield self.env.timeout(1/driving_speed)

    def pick_up_material_on_tr_process(self, tr: TransportRobot):
        loading_speed = self.tr_order_manager.get_loading_speed()
        yield self.env.timeout(loading_speed)
        self.tr_executing_order.pick_up_material_on_tr(tr)
        tr.working_status.status = TransportRobotStatus.MOVING_TO_DROP_OFF

    def tr_process_1(self):
        while True:
            if self.stop_event is False:
                for tr in self.tr_order_manager.tr_list:

                    # kiss
                    # Bedingung: Auftrag wurde beendet or Simulation Startet
                    #   Order list calculate & sort
                    #   loop alle TR
                    #        Wenn TR frei ist:
                    #            TR auftrag zuordnen
                    #            Auftrag löschen
                    #            Process(Auftrag bearbeiten)

                    #        Wenn TR Auftrag hat:
                    #           Tr bearbeiten Auftrag
                    #              Process (Fährt zur pick up station (kann auch 0 Bewegung sein))
                    #              Process (Pick process)
                    #

                    # tr get new order
                    if tr in self.transport_robot_manager.list_tr_rdy_to_get_new_order:
                        self.transport_robot_manager.get_transport_request_list_from_machines()
                        self.transport_robot_manager.get_transport_order_list()
                        if self.transport_robot_manager.get_transport_order_for_tr(tr) is True:
                            tr.working_status.waiting_for_order = False
                            if self.transport_robot_manager.get_path_for_tr_pick_up(tr) is True:
                                self.transport_robot_manager.list_tr_rdy_to_get_new_order.remove(tr)
                                self.transport_robot_manager.list_tr_drive_to_pick_up.append(tr)

                                tr.working_status.driving_to_new_location = True

                    # TR without order get on the right waiting place
                    if tr.working_status.waiting_for_order is True:
                        if self.transport_robot_manager.check_if_tr_is_on_waiting_place(tr) is False:
                            if len(tr.material_store.items) == 0:
                                self.transport_robot_manager.remove_tr_from_every_list(tr)
                                self.transport_robot_manager.list_tr_moving_to_waiting_destination.append(tr)
                                self.transport_robot_manager.get_path_for_waiting_destination(tr)
                                tr.working_status.driving_to_new_location = True
                                self.env.process(self.tr_driving_through_production_to_waiting_destination(tr))

                    # tr drives to pick up station
                    if tr in self.transport_robot_manager.list_tr_drive_to_pick_up:
                        self.transport_robot_manager.list_tr_drive_to_pick_up.remove(tr)
                        self.env.process(self.tr_driving_through_production_to_pick_up(tr))

                    # tr picks up material
                    if tr in self.transport_robot_manager.list_arrived_tr_on_pick_up_destination:
                        self.transport_robot_manager.list_arrived_tr_on_pick_up_destination.remove(tr)
                        self.env.process(self.tr_pick_up_process(tr))

                    # tr drives to unload station
                    if tr in self.transport_robot_manager.list_loaded_tr_drive_to_unload:
                        self.transport_robot_manager.list_loaded_tr_drive_to_unload.remove(tr)
                        self.env.process(self.tr_driving_through_production_to_unload(tr))

                    # tr unloads material
                    if tr in self.transport_robot_manager.list_arrived_tr_on_unload_destination:
                        self.transport_robot_manager.list_arrived_tr_on_unload_destination.remove(tr)
                        self.env.process(self.tr_unload_process(tr))

                self.transport_robot_manager.print_all_lists()
                yield self.env.timeout(1)

    def tr_driving_through_production_to_pick_up(self, tr: TransportRobot):
        driving_speed = self.transport_robot_manager.get_driving_speed_per_cell()
        if tr.working_status.driving_route_pick_up_material is None:
            while True:
                if self.transport_robot_manager.get_path_for_tr_pick_up(tr) is True:
                    break
                yield self.env.timeout(5)

        while True:
            if self.stop_event is False:
                if self.transport_robot_manager.tr_drive_through_production_to_pick_up_destination(tr) is True:
                    break
            yield self.env.timeout(1 / driving_speed)

        self.transport_robot_manager.list_arrived_tr_on_pick_up_destination.append(tr)
        tr.working_status.driving_to_new_location = False

    def tr_driving_through_production_to_unload(self, tr: TransportRobot):
        driving_speed = self.transport_robot_manager.get_driving_speed_per_cell()

        if tr.working_status.driving_route_unload_material is None:
            while True:
                if self.transport_robot_manager.get_path_for_tr_unload(tr) is True:
                    break
                yield self.env.timeout(5)

        while True:
            if self.stop_event is False:
                if self.transport_robot_manager.tr_drive_through_production_to_unload_destination(tr) is True:
                    break
                yield self.env.timeout(1 / driving_speed)

        self.transport_robot_manager.list_arrived_tr_on_unload_destination.append(tr)
        tr.working_status.driving_to_new_location = False

    def tr_pick_up_process(self, tr: TransportRobot):
        loading_speed = self.transport_robot_manager.get_loading_speed()

        if self.transport_robot_manager.pick_up_material_on_tr(tr) is True:
            yield self.env.timeout(loading_speed)

            self.transport_robot_manager.list_loaded_tr_drive_to_unload.append(tr)
            self.transport_robot_manager.get_path_for_tr_unload(tr)

            tr.working_status.driving_to_new_location = True

    def tr_unload_process(self, tr: TransportRobot):
        loading_speed = self.transport_robot_manager.get_loading_speed()
        arrived_tr: list[TransportRobot]
        if self.transport_robot_manager.unload_single_tr(tr) is True:
            yield self.env.timeout(loading_speed)

            tr.working_status.waiting_for_order = True
            tr.transport_order = None
            self.transport_robot_manager.list_tr_rdy_to_get_new_order.append(tr)

    def tr_driving_through_production_to_waiting_destination(self, tr: TransportRobot):
        driving_speed = self.transport_robot_manager.get_driving_speed_per_cell()
        while True:
            if self.stop_event is False:
                if self.transport_robot_manager.tr_drive_through_production_to_waiting_destination(tr):
                    break
                yield self.env.timeout(1 / driving_speed)
        tr.working_status.driving_to_new_location = False
        self.transport_robot_manager.list_tr_rdy_to_get_new_order.append(tr)

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
