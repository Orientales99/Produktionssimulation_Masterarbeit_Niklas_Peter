from collections import defaultdict


import simpy
import networkx as nx
import math
import matplotlib.pyplot as plt

from pathlib import Path
from src import FORCED_DIRECTED_PLACEMENT
from src.entity.intermediate_store import IntermediateStore
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.monitoring.data_analysis.transport_data.material_flow import MaterialFlow
from src.process_logic.topologie_manager.positions_distance_matrix import PositionsDistanceMatrix
from src.production.base.coordinates import Coordinates
from src.production.production import Production
from src.provide_input_data.forced_directed_placement_service import ForcedDirectedPlacementService


class ForcedDirectedPlacement:
    def __init__(self, env: simpy.Environment, production: Production, material_flow: MaterialFlow,
                 position_distance_matrix: PositionsDistanceMatrix):
        self.env = env
        self.production = production
        self.material_flow = material_flow
        self.forced_directed_placement = ForcedDirectedPlacementService()

        self.class_position_distance_matrix = position_distance_matrix
        self.class_position_distance_matrix.start_creating_positions_distance_matrix()

        self.positions_distance_matrix = self.class_position_distance_matrix.positions_distance_matrix

        self.entity_fixed_assignment: list[tuple[str, str]] = []
        self.entity_assignment: list[tuple[str, str]] = []

        self.number_of_iterations = self.forced_directed_placement.get_number_of_iterations()
        self.k = self.forced_directed_placement.get_k()

    def start_fdp_algorithm(self, start_time: int = 0, end_time: int = float('inf')) -> list[tuple[str, str]]:
        self.save_material_flow_matrix(start_time, end_time)
        self.save_fixed_assignment()
        self.run_networkx_force_directed_layout()
        return self.entity_assignment

    def save_material_flow_matrix(self, start_time: int = 0, end_time: int = float('inf')):
        self.material_flow_matrix = self.material_flow.create_material_flow_matrix(start_time, end_time)

    def save_fixed_assignment(self):
        for row in self.class_position_distance_matrix.production.production_layout:
            for cell in row:
                ent = cell.placed_entity
                if isinstance(ent, (Sink, Source)):
                    if cell.cell_id in self.positions_distance_matrix:
                        self.entity_fixed_assignment.append((cell.cell_id, ent.identification_str))
                elif isinstance(ent, Machine) and ent.driving_speed == 0:
                    if cell.cell_id in self.positions_distance_matrix:
                        self.entity_fixed_assignment.append((cell.cell_id, ent.identification_str))

    def run_networkx_force_directed_layout(self):
        # 1. create graph
        G = nx.DiGraph()
        for src, targets in self.material_flow_matrix.items():
            for tgt, weight in targets.items():
                if weight > 0:
                    G.add_edge(src, tgt, weight=weight)

        # 2. starting position
        self.save_starting_positions()
        fixed_nodes = {station for _, station in self.entity_fixed_assignment}
        pos_init = {ent: (coord.x, coord.y) for ent, coord in self.starting_position_entity.items()}

        # 3. Step-by-step calculation with intermediate results
        n_iter = self.number_of_iterations
        k = self.k
        half_iter = n_iter // 2

        # Iteration 0
        self._plot_networkx_positions(G, pos_init, suffix="vor_Iteration_1")

        # half of the iterations
        pos_half = nx.spring_layout(
            G, pos=pos_init, fixed=fixed_nodes,
            iterations=half_iter, k=k, weight='weight', seed=10
        )
        self._plot_networkx_positions(G, pos_half, suffix=f"nach_Iteration_{half_iter}")

        # all Iterationen
        pos_result = nx.spring_layout(
            G, pos=pos_half, fixed=fixed_nodes,
            iterations=n_iter - half_iter, k=k, weight='weight', seed=10
        )
        self._plot_networkx_positions(G, pos_result, suffix=f"nach_Iteration_{n_iter}")

        # 4. Mapping of Grid
        fdp_coords = {ent: Coordinates(x=coord[0], y=coord[1]) for ent, coord in pos_result.items()}
        nearest_mapping = self.map_fdp_coordinates_to_nearest_positions(fdp_coords)
        self.entity_assignment = self._greedy_assignment(nearest_mapping)
        self.entity_assignment = self.validate_and_correct_assignment(self.entity_assignment)

    def save_starting_positions(self):
        self.starting_position_entity = {}
        for eid, cell_list in self.production.entities_located.items():
            if isinstance(cell_list[0].placed_entity, (Machine, IntermediateStore)):
                hor = self.production.get_horizontal_edges_of_coordinates(cell_list)
                ver = self.production.get_vertical_edges_of_coordinates(cell_list)
                self.starting_position_entity[eid] = Coordinates(hor[0], ver[1])
        self.append_sink_starting_position()

    def append_sink_starting_position(self):
        for row in self.production.production_layout:
            for cell in row:
                ent = cell.placed_entity
                if isinstance(ent, (Sink, Source)):
                    self.starting_position_entity[ent.identification_str] = cell.cell_coordinates

    def map_fdp_coordinates_to_nearest_positions(self, fdp_positions: dict[str, Coordinates]) -> dict[str, str]:
        available = set(self.positions_distance_matrix.keys())
        fixed_map = {pos: station for pos, station in self.entity_fixed_assignment}
        used = set(fixed_map.keys())
        free = available - used

        cell_coords = self.get_cell_coordinates_dict()

        for station, coord in fdp_positions.items():
            if station in fixed_map.values():
                continue

            closest_pos, closest_dist = None, float("inf")
            for pos in free:
                cell_coord = cell_coords[pos]
                dx, dy = coord.x - cell_coord.x, coord.y - cell_coord.y
                dist = math.hypot(dx, dy)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_pos = pos

            if closest_pos:
                fixed_map[closest_pos] = station
                free.remove(closest_pos)

        return fixed_map

    def get_cell_coordinates_dict(self) -> dict[str, Coordinates]:
        return {
            cell_id: Coordinates(int(cell_id.split(":")[0]), int(cell_id.split(":")[1]))
            for cell_id in self.positions_distance_matrix.keys()
        }

    def _greedy_assignment(self, mapping: dict[str, str]) -> list[tuple[str, str]]:
        return [(pos, mapping[pos]) for pos in mapping]

    def validate_and_correct_assignment(self, individuum: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """Validates and corrects the final allocation if a position is occupied more than once."""

        position_to_stations = defaultdict(list)
        for pos, station in individuum:
            position_to_stations[pos].append(station)

        # Search for vacant positions
        all_positions = set(self.positions_distance_matrix.keys())
        used_positions = set(position_to_stations.keys())
        free_positions = list(all_positions - used_positions)

        corrected_assignment = []
        for pos, stations in position_to_stations.items():
            if len(stations) == 1:
                corrected_assignment.append((pos, stations[0]))
            else:
                # Double occupancy -> select station with largest material flow, leave weaker ones behind
                station_flows = []
                for station in stations:
                    flow_sum = sum(self.material_flow_matrix.get(station, {}).values()) + \
                               sum(self.material_flow_matrix.get(other_station, {}).get(station, 0)
                                   for other_station in self.material_flow_matrix)
                    station_flows.append((station, flow_sum))

                # Sort by descending flow
                station_flows.sort(key=lambda x: x[1], reverse=True)
                # Best remains in position
                corrected_assignment.append((pos, station_flows[0][0]))
                # All others are reassigned
                for station, _ in station_flows[1:]:
                    if free_positions:
                        new_pos = free_positions.pop(0)
                        corrected_assignment.append((new_pos, station))
                    else:
                        print(f"Warnung: Keine freie Position für Station {station} verfügbar.")

        return corrected_assignment

    def _plot_networkx_positions(self, G: nx.DiGraph, pos: dict[str, tuple[float, float]], suffix: str = ""):
        plt.figure(figsize=(10, 8))
        weights = [G[u][v]['weight'] for u, v in G.edges()]
        nx.draw_networkx(
            G, pos, with_labels=True,
            node_color='skyblue', node_size=700,
            arrows=True, edge_color='gray',
            width=[min(w * 0.1, 3) for w in weights]
        )
        plt.title(f"FDP NetworkX – {suffix.replace('_', ' ')} – Zeit {self.env.now}s")
        filename = f"FDP_Zeit_{self.env.now}s_Iteration_{suffix}.png"
        Path(FORCED_DIRECTED_PLACEMENT).mkdir(parents=True, exist_ok=True)
        plt.savefig(Path(FORCED_DIRECTED_PLACEMENT) / filename)
        plt.close()
