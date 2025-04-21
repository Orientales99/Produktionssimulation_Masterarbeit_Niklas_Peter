import json
import os

from src import ANALYSIS_SOLUTION
from src.entity.machine.machine import Machine
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot
from src.monitoring.converting_classes_to_dict.convert_cell_to_dict import ConvertCellToDict
from src.order_data.production_material import ProductionMaterial
from src.process_logic.working_robot_order_manager import WorkingRobotOrderManager
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.production.production import Production
from src.production.store_manager import StoreManager


class SavingSimulationData:
    production: Production
    store_manager: StoreManager
    convert_cell_to_dict: ConvertCellToDict
    entities_located: {str, list[Cell]}  # {entity.identification_str, list[Cell]}
    list_every_entity_identification_str: list[str]
    saving_entity_data_list: list[Cell]
    wr_on_machine_list: list[WorkingRobot]
    working_robot_order_manager: WorkingRobotOrderManager

    def __init__(self, environment, production, working_robot_order_manager, store_manager):
        self.env = environment
        self.production = production
        self.working_robot_order_manager = working_robot_order_manager
        self.store_manager = store_manager
        self.convert_cell_to_dict = ConvertCellToDict(self.store_manager)

        self.entities_located = self.production.entities_located.copy()
        self.list_every_entity_identification_str = []
        self.saving_entity_data_list = []
        self.wr_on_machine_list = []
        self.simulation_data_list = []

    def save_every_entity_identification_str(self):
        self.entities_located = self.production.entities_located.copy()
        self.list_every_entity_identification_str = list(self.entities_located.keys())

    def save_entity_action(self, entity: Machine | WorkingRobot | TransportRobot):
        cell = self.save_one_cell_from_entity(entity)
        self.append_current_data_to_file_during_simulation(cell)

    def save_one_cell_of_every_entity(self):
        self.saving_entity_data_list = []
        for identification_str in self.list_every_entity_identification_str:
            cell_list = self.entities_located.get(identification_str)
            cell = cell_list[0]
            cell = self.save_one_cell_from_entity(cell.placed_entity)
            self.saving_entity_data_list.append(cell)

    def save_one_cell_from_entity(self, entity: Machine | WorkingRobot | TransportRobot) -> Cell:
        """Saving the cell in the top left corner of each entity."""

        cell_list = self.entities_located.get(entity.identification_str, [])
        horizontal_edges = self.production.get_horizontal_edges_of_coordinates(cell_list)
        vertical_edges = self.production.get_vertical_edges_of_coordinates(cell_list)
        return self.production.get_cell(Coordinates(horizontal_edges[0], vertical_edges[1]))

    def append_current_data_to_file_during_simulation(self, entity_cell: Cell):
        """appending the most important information of every entity. """
        data_entry = {
            "timestamp": self.env.now,
            "entities": [
                self.convert_cell_to_dict.start_converting_cell_during_simulation(entity_cell)
                ]
        }
        self.simulation_data_list.append(data_entry)

    def convert_simulating_entity_data_to_json(self):
        output_file = ANALYSIS_SOLUTION / "simulation_run_data.json"

        if not os.path.exists(output_file):
            with open(output_file, "w") as f:
                json.dump([], f)

        with open(output_file, "r") as f:
            data = json.load(f)

        data.append(self.simulation_data_list)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)

        self.simulation_data_list = []

    def data_of_entities(self):
        """Creating a file with the complete data of every entity"""
        output_file = ANALYSIS_SOLUTION / "entity_data_.json"
        data_entry = {
            "entities": [self.convert_cell_to_dict.start_converting_cell_during_simulation(cell) for cell in
                         self.saving_entity_data_list]
        }

        with open(output_file, "w") as f:
            json.dump([data_entry], f, indent=4)

    def data_order_completed(self, product: ProductionMaterial, quantity: int):
        """Creating a file with every output material and the time"""
        output_file = ANALYSIS_SOLUTION / "data_finished_products_leaving_production.json"
        data_entry = {
            "Time": self.env.now,
            f"{product.production_material_id.name}": quantity,
        }

        if not os.path.exists(output_file):
            with open(output_file, "w") as f:
                json.dump([], f)

        with open(output_file, "r") as f:
            data = json.load(f)

        data.append(data_entry)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)

    def delete_every_json_file_in_anaylsis_solution(self):
        self.create_empty_json_file("simulation_run_data.json")
        self.create_empty_json_file("entity_data_.json")
        self.create_empty_json_file("data_finished_products_leaving_production.json")

    def create_empty_json_file(self, name_of_json_file: str):
        """Creates an empty JSON file and overwrites any existing file at the given path."""

        file_path = ANALYSIS_SOLUTION / name_of_json_file
        data = []

        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
