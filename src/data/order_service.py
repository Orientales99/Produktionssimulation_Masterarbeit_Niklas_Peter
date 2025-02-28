import json

from src import RESOURCES
from src.data.coordinates import Coordinates
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


class OrderService:

    def __init__(self):
        self.data_production_working_robot = None
        self.data_production_transport_robot = None
        self.data_production_machine = None

    def get_file_production_entities(self):
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

    def get_quantity_per_machine_types(self) -> list:
        machine_type_list = []
        for machines in self.data_production_machine["production_machine"]:
            machine_type = (machines["machine_type"], machines["number_of_machines_in_production"])
            machine_type_list.append(machine_type)
        print(len(machine_type_list))
        return machine_type_list


