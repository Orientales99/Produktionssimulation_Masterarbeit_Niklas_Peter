import json
import math

from src import RESOURCES
from src.entity.sink import Sink
from src.entity.source import Source
from src.production.base.cell import Cell
from src.production.production import Production


class PositionsDistanceMatrix:
    """"16 possible Position are estimated. 4x4 Matrix"""
    positions_distance_matrix: dict[str, dict[str, float]]  # Distance between one Location (cell.identification_str and
                                                            # every other Location (cell.identification_str , int = Distance)

    quantity_of_possible_positions: int
    data_position_identification_str_list: list[str]  # str = cell.identification_str
    data_position_cell_list: list[Cell]
    cell_input_output_production: list[Cell]
    list_identification_str_objects: list[str]  # Machine & Intermediate Store

    def __init__(self, production: Production):
        self.production = production

        self.positions_distance_matrix = {}
        self.data_position_identification_str_list = []
        self.data_position_cell_list = []
        self.cell_input_output_production = []

    def start_creating_positions_distance_matrix(self):
        self.get_potential_position_list_from_json()
        self.save_cells()
        self.calculate_manhattan_distance_between_positions()

    def get_potential_position_list_from_json(self):
        with open(RESOURCES / "potential_machine_and_store_positioning.json", 'r', encoding='utf-8') as w:
            self.data_position_identification_str_list = json.load(w)

    def save_cells(self):
        for y in self.production.production_layout:
            for cell in y:
                self.save_cells_with_potential_object_placement(cell)

    def save_cells_goods_receipt(self, cell: Cell):
        """Saving a list[Cell] with Source"""
        if isinstance(cell.placed_entity, Source):
            self.data_position_cell_list.append(cell)
            self.cell_input_output_production.append(cell)

    def save_cells_goods_issuing(self, cell: Cell):
        if isinstance(cell.placed_entity, Sink):
            self.data_position_cell_list.append(cell)
            self.cell_input_output_production.append(cell)

    def save_cells_with_potential_object_placement(self, cell: Cell):
        """Saving a list[Cell] with potential new placement for Machine / IntermediateStore. Only the Cell in the upper
        left corner of the placement area"""
        if cell.cell_id in self.data_position_identification_str_list:
            self.data_position_cell_list.append(cell)

    def calculate_manhattan_distance_between_positions(self):
        for cell_one in self.data_position_cell_list:
            self.positions_distance_matrix[cell_one.cell_id] = {}
            for cell_two in self.data_position_cell_list:
                if cell_one != cell_two:
                    dx = abs(cell_two.cell_coordinates.x - cell_one.cell_coordinates.x)
                    dy = abs(cell_two.cell_coordinates.y - cell_one.cell_coordinates.y)

                    # because driving Robot has to drive around machine/store cannot drive through it
                    if dy == 0:
                        dy = 6
                    distance = dx + dy
                    self.positions_distance_matrix[cell_one.cell_id][cell_two.cell_id] = distance


