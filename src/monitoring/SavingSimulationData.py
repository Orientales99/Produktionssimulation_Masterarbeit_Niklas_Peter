import json
import os

from datetime import date

from matplotlib import pyplot as plt

from src import SIMULATION_OUTPUT_DATA, ENTITIES_DURING_SIMULATION_DATA, MACHINES_DURING_SIMULATION_DATA, \
    TR_DURING_SIMULATION_DATA, WR_DURING_SIMULATION_DATA, SINK_DURING_SIMULATION_DATA, \
    INTERMEDIATE_STORE_DURING_SIMULATION_DATA, PRODUCTION_TOPOLOGY
from src.entity.intermediate_store import IntermediateStore
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot
from src.monitoring.converting_classes_to_dict.convert_cell_to_dict import ConvertCellToDict
from src.monitoring.converting_classes_to_dict.convert_order_to_dict import ConvertOrderToDict
from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial
from src.process_logic.good_receipt import GoodReceipt
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
        self.convert_order_to_dict = ConvertOrderToDict()

        self.entities_located = self.production.entities_located.copy()
        self.list_every_entity_identification_str = []
        self.saving_entity_data_list = []
        self.wr_on_machine_list = []
        self.simulation_machine_data_list = []
        self.simulation_tr_data_list = []
        self.simulation_wr_data_list = []
        self.simulation_sink_data_list = []
        self.simulation_intermediate_store_data_list = []

        self.time_variable_machine = 0
        self.time_variable_tr = 0
        self.time_variable_wr = 0
        self.time_variable_sink = 0
        self.time_variable_intermediate_store = 0

    def save_every_entity_identification_str(self):
        self.entities_located = self.production.entities_located.copy()
        self.list_every_entity_identification_str = list(self.entities_located.keys())

    def save_entity_action(self, entity: Machine | WorkingRobot | TransportRobot | Sink | IntermediateStore):
        cell = None

        if isinstance(entity, WorkingRobot):
            if entity.working_status.last_placement_in_production is not None:
                if len(entity.working_status.last_placement_in_production) != 0:
                    cell = Cell(Coordinates(1, 1), entity)
        if isinstance(entity, Sink):
            cell = self.production.get_cell(self.production.sink_coordinates)
        elif cell is None:
            cell = self.save_one_cell_from_entity(entity)

        self.append_current_data_to_file_during_simulation(cell)

    def save_one_cell_of_every_entity(self):
        self.saving_entity_data_list = []
        for identification_str in self.list_every_entity_identification_str:
            cell_list = self.entities_located.get(identification_str)
            cell = cell_list[0]
            cell = self.save_one_cell_from_entity(cell.placed_entity)
            self.saving_entity_data_list.append(cell)

    def save_one_cell_from_entity(self, entity: Machine | WorkingRobot | TransportRobot | IntermediateStore) -> Cell:
        """Saving the cell in the top left corner of each entity."""

        cell_list = self.production.entities_located.get(entity.identification_str, [])
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
        if isinstance(entity_cell.placed_entity, Machine):
            self.simulation_machine_data_list.append(data_entry)

        if isinstance(entity_cell.placed_entity, TransportRobot):
            self.simulation_tr_data_list.append(data_entry)

        if isinstance(entity_cell.placed_entity, WorkingRobot):
            self.simulation_wr_data_list.append(data_entry)

        if isinstance(entity_cell.placed_entity, Sink):
            self.simulation_sink_data_list.append(data_entry)

        if isinstance(entity_cell.placed_entity, IntermediateStore):
            self.simulation_intermediate_store_data_list.append(data_entry)

    def convert_simulating_machine_data_to_json(self):

        if len(self.simulation_machine_data_list) != 0:
            data_file_name = f"simulation_machine_run_data_from_{self.time_variable_machine}_sec_to_{self.env.now}_sec.json"
            output_file = MACHINES_DURING_SIMULATION_DATA / data_file_name

            if not os.path.exists(output_file):
                with open(output_file, "w") as f:
                    json.dump([], f)

            with open(output_file, "r") as f:
                data = json.load(f)

            data.append(self.simulation_machine_data_list)

            with open(output_file, "w") as f:
                json.dump(data, f, indent=4)

            self.time_variable_machine = self.env.now
            self.simulation_machine_data_list = []

    def convert_simulating_tr_data_to_json(self):

        if len(self.simulation_tr_data_list) != 0:
            data_file_name = f"simulation_tr_run_data_from_{self.time_variable_tr}_sec_to_{self.env.now}_sec.json"
            output_file = TR_DURING_SIMULATION_DATA / data_file_name

            if not os.path.exists(output_file):
                with open(output_file, "w") as f:
                    json.dump([], f)

            with open(output_file, "r") as f:
                data = json.load(f)

            data.append(self.simulation_tr_data_list)

            with open(output_file, "w") as f:
                json.dump(data, f, indent=4)

            self.time_variable_tr = self.env.now
            self.simulation_tr_data_list = []

    def convert_simulating_wr_data_to_json(self):

        if len(self.simulation_wr_data_list) != 0:
            data_file_name = f"simulation_wr_run_data_from_{self.time_variable_wr}_sec_to_{self.env.now}_sec.json"
            output_file = WR_DURING_SIMULATION_DATA / data_file_name

            if not os.path.exists(output_file):
                with open(output_file, "w") as f:
                    json.dump([], f)

            with open(output_file, "r") as f:
                data = json.load(f)

            data.append(self.simulation_wr_data_list)

            with open(output_file, "w") as f:
                json.dump(data, f, indent=4)

            self.time_variable_wr = self.env.now
            self.simulation_wr_data_list = []

    def convert_simulating_sink_data_to_json(self):
        if len(self.simulation_sink_data_list) != 0:
            data_file_name = f"simulation_sink_run_data_from_{self.time_variable_sink}_sec_to_{self.env.now}_sec.json"
            output_file = SINK_DURING_SIMULATION_DATA / data_file_name

            if not os.path.exists(output_file):
                with open(output_file, "w") as f:
                    json.dump([], f)

            with open(output_file, "r") as f:
                data = json.load(f)

            data.append(self.simulation_sink_data_list)

            with open(output_file, "w") as f:
                json.dump(data, f, indent=4)

            self.time_variable_sink = self.env.now
            self.simulation_sink_data_list = []

    def convert_simulating_intermediate_store_data_to_json(self):
        if len(self.simulation_intermediate_store_data_list) != 0:
            data_file_name = f"simulation_intermediate_store_run_data_from_{self.time_variable_intermediate_store}_sec_to_{self.env.now}_sec.json"
            output_file = INTERMEDIATE_STORE_DURING_SIMULATION_DATA / data_file_name

            if not os.path.exists(output_file):
                with open(output_file, "w") as f:
                    json.dump([], f)

            with open(output_file, "r") as f:
                data = json.load(f)

            data.append(self.simulation_intermediate_store_data_list)

            with open(output_file, "w") as f:
                json.dump(data, f, indent=4)

            self.time_variable_intermediate_store = self.env.now
            self.simulation_intermediate_store_data_list = []

    def data_of_entities(self):
        """Creating a file with the complete data of every entity"""
        output_file = ENTITIES_DURING_SIMULATION_DATA / "entity_starting_data.json"
        data_entry = {
            "entities": [self.convert_cell_to_dict.start_converting_cell_during_simulation(cell) for cell in
                         self.saving_entity_data_list]
        }

        with open(output_file, "w") as f:
            json.dump([data_entry], f, indent=4)

    def data_order_completed(self, product: ProductionMaterial, quantity: int):
        """Creating a file with every output material and the time"""
        output_file = SIMULATION_OUTPUT_DATA / "data_finished_products_leaving_production.json"
        data_entry = {
            "Time": self.env.now,
            f"Product Group": product.production_material_id.name,
            f"Quantity": quantity
        }

        if not os.path.exists(output_file):
            with open(output_file, "w") as f:
                json.dump([], f)

        with open(output_file, "r") as f:
            data = json.load(f)

        data.append(data_entry)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)

    def data_goods_receipt(self, goods_receipt: GoodReceipt):
        """Creating a file with every input material (in production) and the time"""
        output_file = SIMULATION_OUTPUT_DATA / "data_goods_entering_production.json"
        data_entry = {
            "Time": goods_receipt.time,
            f"Product Group": goods_receipt.production_material.production_material_id.name,
            f"Quantity": goods_receipt.quantity
        }

        if not os.path.exists(output_file):
            with open(output_file, "w") as f:
                json.dump([], f)

        with open(output_file, "r") as f:
            data = json.load(f)

        data.append(data_entry)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)

    def save_daily_manufacturing_plan(self, current_date: date, daily_manufacturing_plan: list[Order]):
        """Saves the daily production plan in a JSON file with a date in the file name."""

        filename = f"daily_plan_{current_date.isoformat()}.json"
        output_path = os.path.join(SIMULATION_OUTPUT_DATA / "daily_plans", filename)

        # Unterordner erstellen, falls nicht vorhanden
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        converted_plan = [self.convert_order_to_dict.order_to_dict(order) for order in daily_manufacturing_plan]

        plan_data = {
            "date": current_date.isoformat(),
            "plan": converted_plan
        }

        with open(output_path, "w") as f:
            json.dump(plan_data, f, indent=2)

    def save_daily_topology(self, entity_assignment: list[tuple[str, str]], max_coordinates: Coordinates):
        fig, ax = plt.subplots(figsize=(12, 10))

        #  Define colours (RGB scaled to 0-1)
        machine_color = (116 / 255, 33 / 255, 40 / 255)
        store_color = (161 / 255, 204 / 255, 201 / 255)

        #  Dummy handles for the legend
        machine_handle = None
        store_handle = None

        for cell_id_str, station_id_str in entity_assignment:
            try:
                x_str, y_str = cell_id_str.split(":")
                x, y = int(x_str), int(y_str)
            except ValueError:
                print(f"Ungültiges cell.identification_str: {cell_id_str}")
                continue

            if station_id_str.startswith("Ma"):
                color = machine_color
                label = "Machine"
                if machine_handle is None:
                    machine_handle = ax.plot(x, y, 'o', color=color, label=label)[0]
                else:
                    ax.plot(x, y, 'o', color=color)
            else:
                color = store_color
                label = "Zwischenlager"
                if store_handle is None:
                    store_handle = ax.plot(x, y, 'o', color=color, label=label)[0]
                else:
                    ax.plot(x, y, 'o', color=color)

            ax.text(x + 0.2, y + 0.2, station_id_str, fontsize=9)

        #  Axis labelling and limits
        ax.set_xlim(left=0, right=max_coordinates.x + 1)
        ax.set_ylim(bottom=0, top=max_coordinates.y + 1)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(f"Produktions-Topologie bei Produktionszeit {self.env.now}")
        ax.grid(True)
        ax.set_aspect('equal', adjustable='box')

        #  Add legend if handles exist
        handles = [h for h in [machine_handle, store_handle] if h is not None]
        if handles:
            ax.legend()

        # Create memory path
        os.makedirs(PRODUCTION_TOPOLOGY, exist_ok=True)
        file_path = os.path.join(PRODUCTION_TOPOLOGY, f"topology_{int(self.env.now)}.png")
        plt.savefig(file_path)
        plt.close()



