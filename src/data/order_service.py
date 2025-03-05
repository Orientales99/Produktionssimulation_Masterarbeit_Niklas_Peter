import json

from simpy import Container

from src import RESOURCES
from src.data.constant import MachineQuality
from src.data.coordinates import Coordinates
from src.data.simulation_environment import SimulationEnvironment
from src.data.machine import Machine
from src.data.machine_storage import MachineStorage
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


class OrderService:

    def __init__(self):
        self.data_production_working_robot = None
        self.data_production_transport_robot = None
        self.data_production_machine = None
        self.data_process_starting_conditions = None
        self.env = SimulationEnvironment()

    def get_files_for_init(self):
        with open(RESOURCES / "simulation_production_working_robot_data.json", 'r', encoding='utf-8') as w:
            self.data_production_working_robot = json.load(w)

        with open(RESOURCES / "simulation_production_transport_robot_data.json", 'r', encoding='utf-8') as t:
            self.data_production_transport_robot = json.load(t)

        with open(RESOURCES / "simulation_production_machine_data.json", 'r', encoding='utf-8') as m:
            self.data_production_machine = json.load(m)

        with open(RESOURCES / "simulation_starting_conditions.json", 'r', encoding='utf-8') as psc:
            self.data_process_starting_conditions = json.load(psc)

    def get_quantity_of_wr(self) -> int:
        working_robot_stats = self.data_production_working_robot["working_robot"][0]
        return int(working_robot_stats["number_of_robots_in_production"])

    def create_wr(self, identification_number) -> WorkingRobot:
        working_robot_stats = self.data_production_working_robot["working_robot"][0]
        return WorkingRobot(identification_number,
                            robot_size=Coordinates(int(working_robot_stats["robot_size_x"]),
                                                   int(working_robot_stats["robot_size_y"])),
                            driving_speed=working_robot_stats["driving_speed"],
                            product_transfer_rate=working_robot_stats[
                                "product_transfer_rate_units_per_minute"])

    def generate_wr_list(self) -> list:
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
        return TransportRobot(identification_number, None,
                              Coordinates(int(transport_robot_stats["robot_size_x"]),
                                          int(transport_robot_stats["robot_size_y"])),
                              transport_robot_stats["driving_speed"], transport_robot_stats["loaded_capacity"],
                              transport_robot_stats["max_loading_capacity"])

    def generate_tr_list(self) -> list:
        tr_list = []
        quantity_of_tr = self.get_quantity_of_tr()
        for x in range(0, quantity_of_tr):
            tr_list.append(self.create_tr(x + 1))
        return tr_list

    def get_quantity_per_machine_types_list(self) -> list:
        machine_type_list = []
        for machines in self.data_production_machine["production_machine"]:
            machine_type = (machines["machine_type"], machines["number_of_machines_in_production"])
            machine_type_list.append(machine_type)
        return machine_type_list

    def create_machine(self, machine_type, identification_number, machine_quality) -> Machine:
        machine_stats = self.data_production_machine["production_machine"][machine_type]
        return Machine(machine_type, identification_number, MachineQuality(machine_quality),
                       machine_stats["driving_speed"],
                       machine_stats["working_speed"],
                       Coordinates(int(machine_stats["robot_size_x"]), int(machine_stats["robot_size_y"])), MachineStorage(
                Container(self.env, int(machine_stats["max_loading_capacity_product_before_process"]),
                          int(machine_stats["quantity_loaded_product_before_processed"])), None,
                Container(self.env, int(machine_stats["max_loading_capacity_product_after_process"]),
                          int(machine_stats["quantity_loaded_product_after_processed"])), None),
                       False, None,
                       machine_stats["setting_up_time"])

    def generate_machine_list(self) -> list:
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

    def set_max_coordinates_for_production_layout(self) -> Coordinates:
        return Coordinates(int(self.data_process_starting_conditions["production_layout_size_x"]),
                           int(self.data_process_starting_conditions["production_layout_size_y"]))

    def set_visualising_via_terminal(self):
        if self.data_process_starting_conditions["visualising_via_terminal(y/n)"] == "y":
            return True
        else:
            return False

    def set_visualising_via_matplotlib(self):
        if self.data_process_starting_conditions["visualising_via_matplotlib(y/n)"] == "y":
            return True
        else:
            return False