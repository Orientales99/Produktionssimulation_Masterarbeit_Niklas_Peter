import simpy

from src.constant.constant import WorkingRobotStatus, MachineWorkingRobotStatus
from src.entity.working_robot.working_robot import WorkingRobot
from src.monitoring.SavingSimulationData import SavingSimulationData
from src.process_logic.working_robot_order_manager import WorkingRobotOrderManager
from src.simulation_environmnent.simulation_control import SimulationControl


class WrSimulation:
    def __init__(self, env: simpy.Environment, working_robot_order_manager: WorkingRobotOrderManager,
                 saving_simulation_data: SavingSimulationData, simulation_control: SimulationControl):
        self.env = env
        self.working_robot_order_manager = working_robot_order_manager
        self.saving_simulation_data = saving_simulation_data
        self.simulation_control = simulation_control

    def start_every_wr_process(self):
        while True:
            if self.simulation_control.stop_event is False and \
                    self.simulation_control.stop_production_processes is False:

                self.working_robot_order_manager.sort_process_order_list_for_wr()
                self.working_robot_order_manager.every_idle_wr_get_order()

                for wr in self.working_robot_order_manager.wr_list:

                    # get driving route
                    if wr.working_status.status == WorkingRobotStatus.WAITING_FREE_DRIVING_ROUTE and \
                            wr.working_status.working_on_status is False:
                        wr.working_status.working_on_status = True
                        if self.working_robot_order_manager.get_path_for_wr(wr) is True:
                            wr.working_status.working_on_status = False
                            wr.working_status.status = WorkingRobotStatus.MOVING_TO_MACHINE
                        else:
                            wr.working_status.working_on_status = False

                    # wr drives to waiting location
                    if wr.working_status.status == WorkingRobotStatus.IDLE and \
                            wr.working_status.working_on_status is False and \
                            self.working_robot_order_manager.check_if_tr_is_on_waiting_place(wr) is False:
                        wr.working_status.status = WorkingRobotStatus.RETURNING
                        wr.working_status.working_on_status = True
                        if self.working_robot_order_manager.start__moving_to_waiting__process_for_wr(wr):
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
                        if self.working_robot_order_manager.wr_driving_in_machine(wr) is True:
                            wr.working_status.status = WorkingRobotStatus.WORKING_ON_MACHINE
                            self.saving_simulation_data.save_entity_action(wr)

                    # working process on the machine happens in the class machine_execution

                    # wr drives off the machine
                    if wr.working_status.status == WorkingRobotStatus.WAITING_IN_MACHINE_TO_EXIT and \
                            wr.working_status.working_on_status is False:
                        self.env.process(self.wr_exit_machine_process(wr))
                yield self.env.timeout(1)
            else:
                yield self.env.timeout(1)

    def drive_wr_to_destination_process(self, wr: WorkingRobot):
        driving_speed = self.working_robot_order_manager.get_driving_speed_per_cell()

        while True:
            if self.simulation_control.stop_event is False and \
                    self.simulation_control.stop_production_processes is False:
                driving_bool = self.working_robot_order_manager.drive_wr_one_step_trough_production(wr)
                if driving_bool is True:
                    if wr.working_status.status == WorkingRobotStatus.MOVING_TO_MACHINE:
                        wr.working_status.status = WorkingRobotStatus.WAITING_IN_FRONT_OF_MACHINE
                        wr.working_status.working_on_status = False
                        self.saving_simulation_data.save_entity_action(wr)
                        break

                    elif wr.working_status.status == WorkingRobotStatus.RETURNING:
                        wr.working_status.status = WorkingRobotStatus.IDLE
                        wr.working_status.working_on_status = False
                        self.saving_simulation_data.save_entity_action(wr)
                        break

                elif driving_bool is Exception:
                    yield self.env.timeout(2)

            self.saving_simulation_data.save_entity_action(wr)
            yield self.env.timeout(1 / driving_speed)

        yield self.env.timeout(1)

    def wr_exit_machine_process(self, wr: WorkingRobot):
        while True:
            wr_is_off_machine = self.working_robot_order_manager.wr_driving_off_machine(wr)
            if wr_is_off_machine is True:
                wr.working_status.working_for_machine.working_status.working_robot_status = \
                    MachineWorkingRobotStatus.NO_WR

                wr.working_status.working_for_machine = None
                wr.working_status.driving_destination_coordinates = None
                wr.working_status.driving_route = None
                wr.working_status.last_placement_in_production = None

                wr.working_status.status = WorkingRobotStatus.IDLE
                wr.working_status.working_on_status = False
                self.saving_simulation_data.save_entity_action(wr)
                break

            yield self.env.timeout(2)
