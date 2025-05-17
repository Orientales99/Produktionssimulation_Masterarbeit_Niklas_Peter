import simpy

from src.constant.constant import MachineProcessStatus, MachineWorkingRobotStatus, MachineStorageStatus
from src.entity.machine.machine import Machine
from src.monitoring.SavingSimulationData import SavingSimulationData
from src.process_logic.machine.machine_execution import MachineExecution
from src.process_logic.machine.machine_manager import MachineManager
from src.production.production import Production
from src.production.store_manager import StoreManager
from src.simulation_environmnent.simulation_control import SimulationControl


class MachineSimulation:
    def __init__(self, env: simpy.Environment, production: Production, machine_manager: MachineManager,
                 machine_execution: MachineExecution, store_manager: StoreManager,
                 saving_simulation_data: SavingSimulationData, simulation_control: SimulationControl):
        self.env = env
        self.production = production
        self.machine_manager = machine_manager
        self.machine_execution = machine_execution
        self.store_manager = store_manager
        self.saving_simulation_data = saving_simulation_data
        self.simulation_control = simulation_control

    def run_machine_process(self):
        while True:
            if self.simulation_control.stop_event is False and \
                    self.simulation_control.stop_production_processes is False:
                for machine in self.production.machine_list:

                    # set machine process status: idle
                    if len(machine.processing_list) == 0:
                        machine.working_status.process_status = MachineProcessStatus.IDLE
                        self.saving_simulation_data.save_entity_action(machine)

                    # set machine process status: waiting next order
                    if len(machine.processing_list) != 0 and \
                            machine.working_status.process_status == MachineProcessStatus.IDLE:
                        machine.working_status.process_status = MachineProcessStatus.WAITING_NEXT_ORDER
                        self.saving_simulation_data.save_entity_action(machine)

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
            self.saving_simulation_data.save_entity_action(machine)

    def producing_process(self, machine: Machine):
        required_material = machine.process_material_list[0].required_material
        producing_material = machine.process_material_list[0].producing_material

        # get a new order for the next producing step of the machine
        self.machine_execution.give_order_to_next_machine(producing_material, machine)

        while True:
            if self.simulation_control.stop_event is False and \
                    self.simulation_control.stop_production_processes is False:
                # check if space is in output_store
                if self.store_manager.count_empty_space_in_store(machine.machine_storage.storage_after_process) == 0 \
                        or self.store_manager.check_no_other_material_is_in_store(
                    machine.machine_storage.storage_after_process, producing_material) is False and \
                        machine.working_status.process_status != MachineProcessStatus.FINISHED_TO_PRODUCE:
                    machine.working_status.process_status = MachineProcessStatus.PRODUCING_PAUSED
                    machine.working_status.storage_status = MachineStorageStatus.OUTPUT_FULL
                    self.saving_simulation_data.save_entity_action(machine)

                    yield self.env.timeout(1)

                # check if material is in input_store
                elif self.machine_manager.check_required_material_in_storage_before_process(machine,
                                                                                            required_material) is False \
                        and machine.working_status.process_status != MachineProcessStatus.FINISHED_TO_PRODUCE:
                    machine.working_status.process_status = MachineProcessStatus.PRODUCING_PAUSED
                    machine.working_status.storage_status = MachineStorageStatus.INPUT_EMPTY

                    self.saving_simulation_data.save_entity_action(machine)
                    yield self.env.timeout(1)

                elif machine.working_status.process_status != MachineProcessStatus.FINISHED_TO_PRODUCE:
                    machine.working_status.process_status = MachineProcessStatus.READY_TO_PRODUCE
                    machine.working_status.storage_status = MachineStorageStatus.STORAGES_READY_FOR_PRODUCTION
                    self.saving_simulation_data.save_entity_action(machine)

                elif machine.working_status.process_status == MachineProcessStatus.FINISHED_TO_PRODUCE:
                    machine.working_status.working_on_status = False
                    if len(machine.processing_list) == 0:
                        machine.working_status.process_status = MachineProcessStatus.IDLE
                    else:
                        machine.working_status.process_status = MachineProcessStatus.WAITING_NEXT_ORDER
                    self.saving_simulation_data.save_entity_action(machine)
                    break

                else:
                    raise Exception(self.env.now)

                # start producing process und einen begriff für den Process in
                if machine.working_status.process_status == MachineProcessStatus.READY_TO_PRODUCE and \
                        machine.working_status.working_robot_status == MachineWorkingRobotStatus.WR_PRESENT:
                    machine.working_status.process_status = MachineProcessStatus.PRODUCING_PRODUCT

                    if machine.working_status.producing_item is False:
                        machine.working_status.producing_item = True
                        self.env.process(self.machine_execution.produce_one_item(machine, required_material,
                                                                                 producing_material))
                    self.saving_simulation_data.save_entity_action(machine)
            yield self.env.timeout(1)
