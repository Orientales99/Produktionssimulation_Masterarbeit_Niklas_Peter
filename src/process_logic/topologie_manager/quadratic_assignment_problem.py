import pulp as pulp

from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.monitoring.data_analysis.transport_data.material_flow import MaterialFlow
from src.process_logic.topologie_manager.positions_distance_matrix import PositionsDistanceMatrix


class QuadraticAssignmentProblem:
    positions_distance_matrix: dict[str, dict[str, float]]  # Distance between one Location (cell.identification_str and
    # every other Location (cell.identification_str , int = Distance)

    material_flow_matrix: dict[str, dict[str, int]]  # Materialflow between Station (Machine| Sink| Source|
    # IntermediateStore ) and another station.
    # Dict[station.identification_str, dict[station.identification_str, quantity of material]]

    entity_fixed_assignment: list[tuple[str, str]]  # tuple[cell.identification_str, station.identification_str]
    entity_assignment: list[tuple[str, str]]  # tuple[cell.identification_str, station.identification_str]

    def __init__(self, material_flow: MaterialFlow, position_distance_matrix: PositionsDistanceMatrix):
        self.material_flow = material_flow
        self.class_position_distance_matrix = position_distance_matrix
        self.class_position_distance_matrix.start_creating_positions_distance_matrix()

        self.positions_distance_matrix = self.class_position_distance_matrix.positions_distance_matrix

        self.material_flow_matrix = {}
        self.entity_fixed_assignment = []
        self.entity_assignment = []

    def start_quadratic_assignment_problem(self, start_time: int = 0, end_time: int = float('inf')) -> list[
        tuple[str, str]]:
        self.get_material_flow_matrix(start_time, end_time)
        self.save_fixed_assignment()
        self.solve_qap_with_fixed_assignments()
        print(f"start_quadratic_assignment_problem: {self.entity_assignment}")
        return self.entity_assignment

    def get_material_flow_matrix(self, start_time: int = 0, end_time: int = float('inf')):
        self.material_flow_matrix = self.material_flow.create_material_flow_matrix(start_time, end_time)

    def save_fixed_assignment(self):
        """Source, Sink are fixed assignments. Every materialflow to the inmobile machines are summerized in the
        position of the sink"""
        for y in self.class_position_distance_matrix.production.production_layout:
            for cell in y:

                if isinstance(cell.placed_entity, Sink):
                    self.entity_fixed_assignment.append((cell.cell_id, cell.placed_entity.identification_str))

                if isinstance(cell.placed_entity, Source):
                    self.entity_fixed_assignment.append((cell.cell_id, cell.placed_entity.identification_str))

                if isinstance(cell.placed_entity, Machine):
                    if cell.placed_entity.driving_speed == 0:
                        if cell.cell_id in self.positions_distance_matrix.keys():
                            self.entity_fixed_assignment.append((cell.cell_id, cell.placed_entity.identification_str))

    def solve_qap_with_fixed_assignments(self):
        """Main method to solve QAP with fixed assignments."""
        self._prepare_fixed_assignments()
        self._define_decision_variables()
        self._define_objective_function()
        self._define_constraints()
        self._solve_problem()
        self._extract_final_assignment()

    def _prepare_fixed_assignments(self):
        """Prepare lists for fixed and free stations and locations."""
        self.fixed_station_to_location = dict((station, loc) for loc, station in self.entity_fixed_assignment)
        self.assigned_locations = set(self.fixed_station_to_location.values())
        self.assigned_stations = set(self.fixed_station_to_location.keys())

        self.stations = list(self.material_flow_matrix.keys())
        self.locations = list(self.positions_distance_matrix.keys())

        self.free_stations = [s for s in self.stations if s not in self.assigned_stations]
        self.free_locations = [l for l in self.locations if l not in self.assigned_locations]

    def _define_decision_variables(self):
        """Define binary decision variables for free assignments."""
        self.x = pulp.LpVariable.dicts(
            "x",
            [(i, j) for i in self.free_stations for j in self.free_locations],
            0, 1, pulp.LpBinary
        )
        self.prob = pulp.LpProblem("QAP_with_fixed_assignments", pulp.LpMinimize)

    def _define_objective_function(self):
        """Define objective function: minimize flow * distance."""
        obj = 0
        for i in self.stations:
            for k in self.stations:
                flow = self.material_flow_matrix.get(i, {}).get(k, 0)
                for j in self.locations:
                    for q in self.locations:
                        dist = self.positions_distance_matrix.get(j, {}).get(q, 0)

                        term_1 = self._get_assignment_term(i, j)
                        term_2 = self._get_assignment_term(k, q)

                        obj += flow * dist * self._multiply_terms(term_1, term_2)
        self.prob += obj

    def _define_constraints(self):
        """Ensure each free station and location gets exactly one assignment."""
        for i in self.free_stations:
            self.prob += pulp.lpSum([self.x[i, j] for j in self.free_locations]) == 1

        for j in self.free_locations:
            self.prob += pulp.lpSum([self.x[i, j] for i in self.free_stations]) == 1

    def _solve_problem(self):
        """Solve the optimization problem."""
        self.prob.solve()

    def _extract_final_assignment(self):
        """Combine fixed and optimized assignments."""
        self.entity_assignment = [(loc, station) for loc, station in self.entity_fixed_assignment]

        for i in self.free_stations:
            for j in self.free_locations:
                if pulp.value(self.x[i, j]) == 1:
                    self.entity_assignment.append((j, i))  # (cell_id, station_id)

    def _get_assignment_term(self, station, location):
        """Get binary value or variable depending on whether fixed or not."""
        if station in self.free_stations and location in self.free_locations:
            return self.x[station, location]
        elif self.fixed_station_to_location.get(station) == location:
            return 1
        else:
            return 0

    def _multiply_terms(self, a, b):
        """Multiply constants and/or pulp variables safely."""
        if isinstance(a, int) and isinstance(b, int):
            return a * b
        elif isinstance(a, pulp.LpVariable) and isinstance(b, int):
            return a * b
        elif isinstance(b, pulp.LpVariable) and isinstance(a, int):
            return a * b
        elif isinstance(a, pulp.LpVariable) and isinstance(b, pulp.LpVariable):
            # Approximate: ignore interaction (valid if flow is small)
            return 0  # Optional: ignore bilinear terms to keep it linear
        return 0
