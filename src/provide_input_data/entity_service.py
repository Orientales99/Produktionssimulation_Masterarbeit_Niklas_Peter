import json

from simpy import Store

from src import RESOURCES
from src.constant.constant import MachineQuality, TransportRobotStatus, WorkingRobotStatus, MachineProcessStatus, \
    MachineWorkingRobotStatus
from src.entity.machine.machine_working_status import MachineWorkingStatus
from src.entity.working_robot.wr_working_status import WrWorkingStatus
from src.production.base.coordinates import Coordinates
from src.entity.transport_robot.tr_working_status import TrWorkingStatus
from src.entity.machine.machine import Machine
from src.entity.machine.machine_storage import MachineStorage
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot


class EntityService:

    def __init__(self, simulation_environment):
        self.env = simulation_environment
        self.data_production_working_robot = None
        self.data_production_transport_robot = None
        self.data_production_machine = None

        self.get_entity_files_for_init()

    def get_entity_files_for_init(self):
        with open(RESOURCES / "simulation_production_working_robot_data.json", 'r', encoding='utf-8') as w:
            self.data_production_working_robot = json.load(w)
        with open(RESOURCES / "simulation_production_transport_robot_data.json", 'r', encoding='utf-8') as t:
            self.data_production_transport_robot = json.load(t)
        with open(RESOURCES / "simulation_production_machine_data.json", 'r', encoding='utf-8') as m:
            self.data_production_machine = json.load(m)

    def get_quantity_of_wr(self) -> int:
        working_robot_stats = self.data_production_working_robot["working_robot"][0]
        return int(working_robot_stats["number_of_robots_in_production"])

    def create_wr(self, identification_number) -> WorkingRobot:
        working_robot_stats = self.data_production_working_robot["working_robot"][0]

        waiting_time = int(identification_number) * 2

        return WorkingRobot(identification_number,
                            Coordinates(
                                int(working_robot_stats["robot_size_x"]),
                                int(working_robot_stats["robot_size_y"])),
                            working_robot_stats["driving_speed"],
                            working_robot_stats["product_transfer_rate_units_per_minute"],
                            WrWorkingStatus(WorkingRobotStatus.IDLE, False, False, waiting_time, None, None, None,
                                            None))

    def generate_wr_list(self) -> list[WorkingRobot]:

        wr_list = []

        quantity_of_wr = self.get_quantity_of_wr()
        for x in range(0, quantity_of_wr):
            wr_list.append(self.create_wr(x + 1))
        return wr_list

    def get_quantity_of_tr(self) -> int:
        transport_robot_stats = self.data_production_transport_robot["transport_robot"][0]
        return int(transport_robot_stats["number_of_robots_in_production"])

    def create_tr(self, identification_number) -> TransportRobot:
        transport_robot_stats = self.data_production_transport_robot["transport_robot"][0]
        waiting_time = int(identification_number) * 2

        return TransportRobot(identification_number,
                              Coordinates(
                                  int(transport_robot_stats["robot_size_x"]),
                                  int(transport_robot_stats["robot_size_y"])),
                              int(transport_robot_stats["loading_speed"]),
                              transport_robot_stats["driving_speed"],
                              Store(
                                  self.env,
                                  capacity=int(transport_robot_stats["max_loading_capacity"])),
                              TrWorkingStatus(TransportRobotStatus.IDLE, False, waiting_time, None, None, None))

    def generate_tr_list(self) -> list[TransportRobot]:
        tr_list = []
        quantity_of_tr = self.get_quantity_of_tr()
        for x in range(0, quantity_of_tr):
            tr_list.append(self.create_tr(x + 1))
        return tr_list

    def get_quantity_per_machine_types_list(self) -> list:
        machine_type_list = []
        for machines in self.data_production_machine["production_machine"]:
            machine_type = (int(machines["machine_type"]), int(machines["number_of_machines_in_production"]))
            machine_type_list.append(machine_type)
        return machine_type_list

    def create_machine(self, machine_type, identification_number, machine_quality) -> Machine:
        machine_stats = self.data_production_machine["production_machine"][machine_type]
        return Machine(machine_type,
                       identification_number,
                       MachineQuality(machine_quality),
                       machine_stats["driving_speed"],
                       machine_stats["working_speed"],
                       Coordinates(
                           int(machine_stats["robot_size_x"]),
                           int(machine_stats["robot_size_y"])),
                       MachineStorage(
                           Store(
                               self.env,
                               capacity=int(machine_stats["max_loading_capacity_product_before_process"])),
                           None,
                           Store(
                               self.env,
                               capacity=int(machine_stats["max_loading_capacity_product_after_process"])),
                           None),
                       MachineWorkingStatus(MachineProcessStatus.IDLE, MachineWorkingRobotStatus.NO_WR, False, None,
                                            False),
                       float(machine_stats["setting_up_time"]))

    def generate_machine_list(self) -> list[Machine]:
        machine_list = []
        quantity_of_machines_per_type_list = self.get_quantity_per_machine_types_list()
        quantity_of_types = len(quantity_of_machines_per_type_list)
        for machine_type in range(0, quantity_of_types):
            quantity_of_machines_per_type = int(quantity_of_machines_per_type_list[machine_type][1])
            machines_with_good_quality = int(
                self.data_production_machine["production_machine"][0]["number_of_new_machines"])
            for identification_number in range(0, quantity_of_machines_per_type):
                if machines_with_good_quality > 0:
                    machine_quality = 1
                    machines_with_good_quality -= 1
                else:
                    machine_quality = 0
                machine_list.append(self.create_machine(machine_type, identification_number + 1, machine_quality))
        return machine_list
