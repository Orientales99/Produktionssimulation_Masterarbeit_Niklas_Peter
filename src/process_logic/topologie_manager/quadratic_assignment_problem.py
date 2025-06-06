import copy
import itertools
from collections import defaultdict
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.monitoring.data_analysis.transport_data.material_flow import MaterialFlow
from src.process_logic.topologie_manager.positions_distance_matrix import PositionsDistanceMatrix


class QuadraticAssignmentProblem:
    def __init__(self, material_flow: MaterialFlow, position_distance_matrix: PositionsDistanceMatrix):
        self.material_flow = material_flow
        self.class_position_distance_matrix = position_distance_matrix
        self.class_position_distance_matrix.start_creating_positions_distance_matrix()
        self.positions_distance_matrix = self.class_position_distance_matrix.positions_distance_matrix

        self.material_flow_matrix = {}
        self.entity_fixed_assignment = []  # (cell_id, station_id)
        self.entity_assignment = []  # (cell_id, station_id)

        self.assignment_cost_matrix = defaultdict(dict)  # b_ik cost matrix

    def start_quadratic_assignment_problem(self, start_time: int = 0, end_time: int = float('inf')) -> list[tuple[str, str]]:
        self.get_material_flow_matrix(start_time, end_time)
        self.save_fixed_assignment()
        self.solve_qap_with_fixed_assignments()
        self.validate_and_correct_assignment()
        print(f"Optimized layout: {self.entity_assignment}")
        return self.entity_assignment

    def get_material_flow_matrix(self, start_time: int = 0, end_time: int = float('inf')):
        self.material_flow_matrix = self.material_flow.create_material_flow_matrix(start_time, end_time)

    def save_fixed_assignment(self):
        """Save fixed assignments (e.g., Source, Sink, static Machines)."""
        for y in self.class_position_distance_matrix.production.production_layout:
            for cell in y:
                if isinstance(cell.placed_entity, (Sink, Source)) or (
                        isinstance(cell.placed_entity, Machine) and cell.placed_entity.driving_speed == 0):
                    if cell.cell_id in self.positions_distance_matrix:
                        self.entity_fixed_assignment.append((cell.cell_id, cell.placed_entity.identification_str))


    def solve_qap_with_fixed_assignments(self):
        """
        Solves the quadratic assignment problem considering fixed assignments.
        Objective: Minimize total cost = material_flow * distance.
        Fixed entities (sources, sinks, fixed machines) are pre-assigned and excluded from permutations.
        """

        # All available positions and stations
        all_positions = list(self.positions_distance_matrix.keys())
        all_stations = list(self.material_flow_matrix.keys())

        # Extract fixed assignments
        fixed_positions = set(pos for pos, _ in self.entity_fixed_assignment)
        fixed_stations = set(st for _, st in self.entity_fixed_assignment)

        # Remaining (non-fixed) positions and stations
        free_positions = [pos for pos in all_positions if pos not in fixed_positions]
        free_stations = [st for st in all_stations if st not in fixed_stations]

        best_assignment = []
        best_cost = float('inf')

        # Generate all possible permutations for free stations
        for perm in itertools.permutations(free_positions, len(free_stations)):
            # Build candidate assignment
            candidate_assignment = copy.deepcopy(self.entity_fixed_assignment)
            candidate_assignment.extend(zip(perm, free_stations))

            # Map station to position for fast lookup
            station_to_pos = {station: pos for pos, station in candidate_assignment}

            # Compute total cost
            total_cost = 0.0
            for i in all_stations:
                for j in all_stations:
                    flow = self.material_flow_matrix.get(i, {}).get(j, 0)
                    if flow == 0:
                        continue

                    pos_i = station_to_pos.get(i)
                    pos_j = station_to_pos.get(j)
                    if pos_i is None or pos_j is None:
                        continue

                    distance = self.positions_distance_matrix[pos_i][pos_j]
                    total_cost += flow * distance

            if total_cost < best_cost:
                best_cost = total_cost
                best_assignment = candidate_assignment

        self.entity_assignment = best_assignment

    def validate_and_correct_assignment(self):
        """Validates and corrects final assignments if a position is assigned multiple times."""
        position_to_stations = defaultdict(list)
        for pos, station in self.entity_assignment:
            position_to_stations[pos].append(station)

        all_positions = set(self.positions_distance_matrix.keys())
        used_positions = set(position_to_stations.keys())
        free_positions = list(all_positions - used_positions)

        corrected_assignment = []
        for pos, stations in position_to_stations.items():
            if len(stations) == 1:
                corrected_assignment.append((pos, stations[0]))
            else:
                # Keep the one with the largest flow; reassign others
                station_flows = []
                for station in stations:
                    flow_sum = sum(self.material_flow_matrix.get(station, {}).values()) + \
                               sum(self.material_flow_matrix.get(other, {}).get(station, 0)
                                   for other in self.material_flow_matrix)
                    station_flows.append((station, flow_sum))
                station_flows.sort(key=lambda x: x[1], reverse=True)
                corrected_assignment.append((pos, station_flows[0][0]))
                for station, _ in station_flows[1:]:
                    if free_positions:
                        new_pos = free_positions.pop(0)
                        corrected_assignment.append((new_pos, station))

        self.entity_assignment = corrected_assignment
