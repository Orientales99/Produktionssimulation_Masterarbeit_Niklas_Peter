import json

from src import RESOURCES
from src.data.coordinates import Coordinates
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


class OrderService:

    def __init__(self):
        self.data_production_working_robot = None
        self.data_production_transport_robot = None

    def get_file_production_entities(self):
        with open(RESOURCES / "simulation_production_working_robot_data.json", 'r', encoding='utf-8') as w:
            self.data_production_working_robot = json.load(w)

        with open(RESOURCES / "simulation_production_transport_robot_data.json", 'r', encoding='utf-8') as t:
            self.data_production_transport_robot = json.load(t)

    def get_quantity_of_wr(self):
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

    def generate_wr_list(self):
        wr_list = []

        quantity_of_wr = self.get_quantity_of_wr()
        for x in range(0, quantity_of_wr):
            wr_list.append(self.create_wr(x + 1))
        return wr_list

    def get_quantity_of_tr(self):
        transport_robot_stats = self.data_production_transport_robot["transport_robot"][0]
        return int(transport_robot_stats["number_of_robots_in_production"])

    def create_tr(self, identification_number) -> TransportRobot:
        transport_robot_stats = self.data_production_transport_robot["transport_robot"][0]
        return TransportRobot(identification_number, None,
                              Coordinates(transport_robot_stats["robot_size_y"], transport_robot_stats["robot_size_x"]),
                              transport_robot_stats["driving_speed"], transport_robot_stats["loaded_capacity"],
                              transport_robot_stats["max_loading_capacity"])

    def generate_tr_list(self):
        tr_list = []
        quantity_of_tr = self.get_quantity_of_tr()
        for x in range(0, quantity_of_tr):
            tr_list.append(self.create_tr(x + 1))
        return tr_list
