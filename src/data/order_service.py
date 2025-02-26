import json

from src import RESOURCES
from src.data.working_robot import WorkingRobot


class OrderService:

    def __init__(self):
        self.data_production_working_robot = None

    def get_file_production_entities(self):
        try:
            with open(RESOURCES / "simulation_production_working_robot_data.json", 'r', encoding='utf-8') as f:
                self.data_production_working_robot = json.load(f)
                print("Datei erfolgreich geladen:", f.name)

        except FileNotFoundError:
            print(f"Fehler: Datei '{RESOURCES / "simulation_production_working_robot_data.json"}' nicht gefunden.")
        except json.JSONDecodeError:
            print(
                f"Fehler: Datei '{RESOURCES / "simulation_production_working_robot_data.json"}' enthält ungültiges JSON.")
        except Exception as e:
            print(f"Unerwarteter Fehler: {e}")

    def get_quantity_of_wr(self):
        working_robot_stats = self.data_production_working_robot["working_robot"][0]
        return int(working_robot_stats["number_of_robots_in_production"])

    def create_wr(self, identification_number) -> WorkingRobot:
        working_robot_stats = self.data_production_working_robot["working_robot"][0]
        return WorkingRobot(identification_number, robot_size=working_robot_stats["robot_size_x_y"],
                            driving_speed=working_robot_stats["driving_speed"],
                            product_transfer_rate=working_robot_stats["product_transfer_rate_units_per_minute"])

    def generate_wr_list(self):
        wr_list = []

        quantity_of_wr = self.get_quantity_of_wr()
        print(quantity_of_wr)
        for x in range(0, quantity_of_wr):
            wr_list.append(self.create_wr(x + 1))
        return wr_list
