import random

import simpy

from src.constant.constant import TransportRobotStatus, MachineStorageStatus
from src.entity.machine.machine import Machine
from src.entity.transport_robot.transport_robot import TransportRobot
from src.monitoring.SavingSimulationData import SavingSimulationData
from src.process_logic.transport_robot.tr_executing_order import TrExecutingOrder
from src.process_logic.transport_robot.tr_order_manager import TrOrderManager
from src.simulation_environmnent.simulation_control import SimulationControl


class TrSimulation:
    def __init__(self, env: simpy.Environment, tr_order_manager: TrOrderManager, tr_executing_order: TrExecutingOrder,
                 saving_simulation_data: SavingSimulationData, simulation_control: SimulationControl):
        self.env = env
        self.tr_order_manager = tr_order_manager
        self.tr_executing_order = tr_executing_order
        self.saving_simulation_data = saving_simulation_data
        self.simulation_control = simulation_control

        self.control_value = 1

    def start_every_tr_process(self):
        while True:
            if self.simulation_control.stop_event is False and \
                    self.simulation_control.stop_production_processes is False:

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
                            and tr.working_status.working_on_status is False or \
                            (tr.working_status.waiting_error_time is not None and
                             tr.working_status.waiting_error_time <= self.env.now):

                        tr.working_status.driving_destination_coordinates = None
                        tr.working_status.driving_route = None
                        tr.working_status.destination_location_entity = None

                        if self.tr_executing_order.check_if_tr_is_on_waiting_place(tr) is False:
                            tr.working_status.status = TransportRobotStatus.RETURNING
                            tr.working_status.working_on_status = True
                            if self.tr_executing_order.start__moving_to_waiting__process_for_tr(tr):
                                self.env.process(self.tr_drive_to_destination_process(tr))

            yield self.env.timeout(1)

    def tr_drive_to_destination_process(self, tr: TransportRobot):
        driving_speed = self.tr_order_manager.get_driving_speed_per_cell()

        while True:
            if self.simulation_control.stop_event is False and \
                    self.simulation_control.stop_production_processes is False:
                self.saving_simulation_data.save_entity_action(tr)
                yield self.env.timeout(1 / driving_speed)
                driving_value = self.tr_executing_order.drive_tr_one_step_trough_production(tr)

                if driving_value is True:
                    tr.working_status.waiting_error_time = self.env.now + 60

                    if tr.working_status.status == TransportRobotStatus.MOVING_TO_PICKUP:
                        tr.working_status.status = TransportRobotStatus.LOADING
                        tr.working_status.working_on_status = False
                        self.saving_simulation_data.save_entity_action(tr)
                        break

                    elif tr.working_status.status == TransportRobotStatus.MOVING_TO_DROP_OFF:
                        tr.working_status.status = TransportRobotStatus.UNLOADING
                        tr.working_status.working_on_status = False
                        self.saving_simulation_data.save_entity_action(tr)
                        break

                    elif tr.working_status.status == TransportRobotStatus.RETURNING:
                        tr.working_status.status = TransportRobotStatus.IDLE
                        tr.working_status.waiting_error_time = None
                        tr.working_status.working_on_status = False
                        self.saving_simulation_data.save_entity_action(tr)
                        break

                    else:
                        tr.working_status.working_on_status = False
                        break

                elif driving_value is Exception:
                    if self.control_value % 2 == 0:
                        yield self.env.timeout(60)
                        self.control_value += 1
                    elif self.control_value % 2 != 0:
                        yield self.env.timeout(2)
                        self.control_value += 1
                # tr.working_status.waiting_error_time = self.env.now + 60
            else:
                yield self.env.timeout(1)

    def pick_up_material_on_tr_process(self, tr: TransportRobot):
        loading_speed = self.tr_order_manager.get_loading_speed()

        yield self.env.timeout(loading_speed)

        if self.tr_executing_order.pick_up_material_on_tr(tr):

            tr.working_status.status = TransportRobotStatus.MOVING_TO_DROP_OFF
            tr.working_status.working_on_status = False
            tr.working_status.waiting_error_time = self.env.now + 60

            if isinstance(tr.transport_order.pick_up_station, Machine):
                tr.transport_order.pick_up_station.working_status.waiting_for_arriving_of_tr = False
                if len(tr.transport_order.pick_up_station.machine_storage.storage_after_process.items) == 0:
                    tr.transport_order.pick_up_station.working_status.storage_status = \
                        MachineStorageStatus.STORAGES_READY_FOR_PRODUCTION
            self.saving_simulation_data.save_entity_action(tr)

    def unload_material_off_tr_process(self, tr: TransportRobot):
        loading_speed = self.tr_order_manager.get_loading_speed()
        yield self.env.timeout(loading_speed)

        if self.tr_executing_order.unload_material_off_tr(tr):
            tr.working_status.status = TransportRobotStatus.IDLE
            tr.working_status.working_on_status = False
            tr.working_status.waiting_error_time = self.env.now + 60
            if isinstance(tr.transport_order.unload_destination, Machine):
                tr.transport_order.unload_destination.working_status.waiting_for_arriving_of_tr = False
            self.saving_simulation_data.save_entity_action(tr)
