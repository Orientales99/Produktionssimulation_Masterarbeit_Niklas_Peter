import simpy
import math
import random
import matplotlib.pyplot as plt

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from src import FORCED_DIRECTED_PLACEMENT
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.monitoring.data_analysis.transport_data.material_flow import MaterialFlow
from src.process_logic.topologie_manager.positions_distance_matrix import PositionsDistanceMatrix
from src.production.base.coordinates import Coordinates
from src.production.production import Production
from src.provide_input_data.forced_directed_placement_service import ForcedDirectedPlacementService


class ForcedDirectedPlacement:
    positions_distance_matrix: dict[str, dict[str, float]]  # Distance between one Location (cell.identification_str and
    # every other Location (cell.identification_str , int = Distance)

    material_flow_matrix: dict[str, dict[str, int]]  # Materialflow between Station (Machine| Sink| Source|
    # IntermediateStore) and another station.
    # Dict[station.identification_str, dict[station.identification_str, quantity of material]]

    starting_position_entity: dict[str, Coordinates]  # dict[entity.identification_str, Coordinates]

    entity_fixed_assignment: list[tuple[str, str]]  # tuple[cell.identification_str, station.identification_str]
    entity_assignment: list[tuple[str, str]]  # tuple[cell.identification_str, station.identification_str]

    number_of_iterations: int
    k: float

    def __init__(self, env: simpy.Environment, production: Production, material_flow: MaterialFlow,
                 position_distance_matrix: PositionsDistanceMatrix):
        self.env = env
        self.production = production
        self.material_flow = material_flow
        self.class_position_distance_matrix = position_distance_matrix

        self.forced_directed_placement = ForcedDirectedPlacementService()

        self.positions_distance_matrix = self.class_position_distance_matrix.positions_distance_matrix

        self.entity_fixed_assignment = []
        self.entity_assignment = []

        self.number_of_iterations = self.forced_directed_placement.get_number_of_iterations()
        self.k = self.forced_directed_placement.get_k()

    def start_fdp_algorithm(self, start_time: int = 0, end_time: int = float('inf')) -> list[tuple[str, str]]:
        self.save_material_flow_matrix(start_time, end_time)
        self.save_fixed_assignment()
        self.run_force_directed_placement()
        print(self.entity_assignment)
        return self.entity_assignment

    def save_material_flow_matrix(self, start_time: int = 0, end_time: int = float('inf')):
        self.material_flow_matrix = self.material_flow.create_material_flow_matrix(start_time, end_time)

    def save_fixed_assignment(self):
        for y in self.class_position_distance_matrix.production.production_layout:
            for cell in y:
                if isinstance(cell.placed_entity, (Sink, Source)) or (
                        isinstance(cell.placed_entity, Machine) and cell.placed_entity.driving_speed == 0):
                    if cell.cell_id in self.positions_distance_matrix:
                        self.entity_fixed_assignment.append((cell.cell_id, cell.placed_entity.identification_str))

    def save_starting_positions(self):
        entities_located = self.production.entities_located
        self.starting_position_entity = {}

        for entity_identification_str in entities_located.keys():
            cell_list = entities_located[entity_identification_str]

            horizontal_coordinates = self.production.get_horizontal_edges_of_coordinates(cell_list)
            vertical_coordinates = self.production.get_vertical_edges_of_coordinates(cell_list)

            self.starting_position_entity[entity_identification_str] = Coordinates(horizontal_coordinates[0],
                                                                                   vertical_coordinates[1])
        self.append_sink_starting_position()

    def append_sink_starting_position(self):
        for y in self.production.production_layout:
            for cell in y:
                if isinstance(cell.placed_entity, Sink):
                    self.starting_position_entity[cell.placed_entity.identification_str] = cell.cell_coordinates
                if isinstance(cell.placed_entity, Source):
                    self.starting_position_entity[cell.placed_entity.identification_str] = cell.cell_coordinates

    def run_force_directed_placement(self):
        """
        Execute the force-directed placement algorithm with fixed and movable nodes.
        Save plots at mid and final iteration. Assign closest cell positions to result.
        """
        # Initialization
        self.save_starting_positions()
        positions = self.starting_position_entity.copy()
        fixed_entities = {station for _, station in self.entity_fixed_assignment}

        for iteration in range(1, self.number_of_iterations + 1):
            displacements = {entity: Coordinates(0, 0) for entity in positions if entity not in fixed_entities}

            # Apply repulsive forces
            for v in positions:
                if v in fixed_entities:
                    continue
                for u in positions:
                    if u == v:
                        continue
                    dx = positions[v].x - positions[u].x
                    dy = positions[v].y - positions[u].y
                    dist = math.hypot(dx, dy) + 1e-5
                    force = self.k ** 2 / dist
                    displacements[v].x += dx / dist * force
                    displacements[v].y += dy / dist * force

            # Apply attractive forces based on material flow
            for v in self.material_flow_matrix:
                for u in self.material_flow_matrix[v]:
                    if v == u:
                        continue
                    flow = self.material_flow_matrix[v][u]
                    dx = positions[v].x - positions[u].x
                    dy = positions[v].y - positions[u].y
                    dist = math.hypot(dx, dy) + 1e-5
                    max_dist = 1e6  # Setze nach Bedarf realistisch basierend auf deiner Layoutgröße
                    dist_capped = min(dist, max_dist)

                    try:
                        force = (dist_capped ** 2) / self.k * flow
                    except OverflowError:
                        force = float("inf")

                    if v not in fixed_entities:
                        displacements[v].x -= dx / dist * force
                        displacements[v].y -= dy / dist * force
                    if u not in fixed_entities:
                        displacements[u].x += dx / dist * force
                        displacements[u].y += dy / dist * force

            # Update positions
            for entity in positions:
                if entity not in fixed_entities:
                    positions[entity].x += displacements[entity].x
                    positions[entity].y += displacements[entity].y

            # Save plot at midpoint
            if iteration == self.number_of_iterations // 2:
                self._plot_positions(positions, iteration)

        # Save final iteration plot
        self._plot_positions(positions, self.number_of_iterations)

        # Map continuous FDP positions to discrete cell IDs
        nearest_position_station_dict = self.map_fdp_coordinates_to_nearest_positions(positions)

        # Assign stations to final positions
        self.entity_assignment = self._greedy_assignment(nearest_position_station_dict)
        self.entity_assignment = self.validate_and_correct_assignment(self.entity_assignment)

    def map_fdp_coordinates_to_nearest_positions(self, fdp_positions: dict[str, Coordinates]) -> dict[str, str]:
        """
        Map continuous FDP positions (Coordinates) to nearest available discrete positions (cell identification strings).
        Each station gets assigned to the closest free cell (cell.identification_str).
        Returns a dict: {cell_id (str) -> station_id (str)}.
        """

        # Alle verfügbaren Zellen (cell.identification_str)
        available_positions = set(self.positions_distance_matrix.keys())

        # Fix zugeordnete Positionen aus self.entity_fixed_assignment (cell_id, station_id)
        mapped_result = {pos: station for pos, station in self.entity_fixed_assignment}

        # Positionen, die schon belegt sind
        used_positions = set(mapped_result.keys())

        # Frei verfügbare Zellen
        free_positions = available_positions - used_positions

        cell_coordinates_dict = self.get_cell_coordinates_dict()

        for station, coord in fdp_positions.items():
            # Falls Station schon fix zugeordnet ist, überspringen
            if station in mapped_result.values():
                continue

            closest_pos = None
            closest_dist = float("inf")

            for pos in free_positions:
                # Koordinaten der Zelle aus cell_coordinates_dict holen
                cell_coord = cell_coordinates_dict[pos]  # z.B. Coordinates(x=13, y=15)

                dx = coord.x - cell_coord.x
                dy = coord.y - cell_coord.y
                dist = math.hypot(dx, dy)

                if dist < closest_dist:
                    closest_dist = dist
                    closest_pos = pos

            if closest_pos is not None:
                mapped_result[closest_pos] = station
                free_positions.remove(closest_pos)

        return mapped_result

    def get_cell_coordinates_dict(self) -> dict[str, Coordinates]:
        cell_coordinates_dict = {
            cell_id: Coordinates(int(cell_id.split(":")[0]), int(cell_id.split(":")[1]))
            for cell_id in self.positions_distance_matrix.keys()
        }
        return cell_coordinates_dict

    def _greedy_assignment(self, position_station_dict: dict[str, str]) -> list[tuple[str, str]]:
        """
        Convert position_station_dict into a list of assignments.
        """
        entity_assignment_list: list[tuple[str, str]]
        entity_assignment_list = []

        for position in position_station_dict.keys():
            entity_assignment_list.append((position, position_station_dict[position]))

        return entity_assignment_list

    def _plot_positions(self, positions: dict[str, Coordinates], iteration: int):
        """
        Plot the current position of entities and save the image.
        """
        plt.figure(figsize=(10, 8))
        for entity, coord in positions.items():
            plt.scatter(coord.x, coord.y, label=entity)
            plt.text(coord.x, coord.y, entity, fontsize=8)

        plt.title(
            f"Force Directed Placement - Iteration {iteration} - k={self.k} - {datetime.now().strftime('%H-%M-%S')}")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend(loc='upper right', fontsize='small', bbox_to_anchor=(1.15, 1.0))
        plt.grid(True)

        filename = f"FDP_Iteration_{iteration}_k_{self.k}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
        save_path = Path(FORCED_DIRECTED_PLACEMENT) / filename
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path)
        plt.close()

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
