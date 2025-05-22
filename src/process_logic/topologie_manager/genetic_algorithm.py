import simpy
import random
import matplotlib.pyplot as plt
import os
import json
import numpy as np
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.monitoring.data_analysis.transport_data.material_flow import MaterialFlow
from src.process_logic.topologie_manager.positions_distance_matrix import PositionsDistanceMatrix
from src.provide_input_data.genetic_algorithm_service import GeneticAlgorithmService
from src import GENETIC_ALGORITHM


class GeneticAlgorithm:
    positions_distance_matrix: dict[str, dict[str, float]]
    material_flow_matrix: dict[str, dict[str, int]]
    entity_fixed_assignment: list[tuple[str, str]]
    entity_assignment: list[tuple[str, str]]

    genetic_algorithm_service: GeneticAlgorithmService

    number_of_iterations: int
    population_size: int
    number_of_surviving_parents: int
    odds_of_mutation_per_genom_in_percent: int
    points_of_separation: int

    def __init__(self, env: simpy.Environment, material_flow: MaterialFlow, position_distance_matrix: PositionsDistanceMatrix):
        self.env = env
        self.material_flow = material_flow
        self.class_position_distance_matrix = position_distance_matrix

        self.positions_distance_matrix = self.class_position_distance_matrix.positions_distance_matrix
        self.entity_fixed_assignment = []
        self.entity_assignment = []

        self.genetic_algorithm_service = GeneticAlgorithmService()
        self.number_of_iterations = self.genetic_algorithm_service.get_number_of_iterations()
        self.population_size = self.genetic_algorithm_service.get_population_size_per_generation()
        self.number_of_surviving_parents = self.genetic_algorithm_service.get_number_of_surviving_parents()
        self.odds_of_mutation_per_genom_in_percent = self.genetic_algorithm_service.get_odds_of_mutation_per_genom_in_percent()
        self.points_of_separation = self.genetic_algorithm_service.get_points_of_separation()

        self.class_position_distance_matrix.start_creating_positions_distance_matrix()

    def start_genetic_algorithm(self, start_time: int = 0, end_time: int = float('inf')):
        self.get_material_flow_matrix(start_time, end_time)
        self.save_fixed_assignment()
        self.run_genetic_loop()
        return self.entity_assignment

    def get_material_flow_matrix(self, start_time: int = 0, end_time: int = float('inf')):
        self.material_flow_matrix = self.material_flow.create_material_flow_matrix(start_time, end_time)

    def save_fixed_assignment(self):
        for y in self.class_position_distance_matrix.production.production_layout:
            for cell in y:
                if isinstance(cell.placed_entity, (Sink, Source)) or (isinstance(cell.placed_entity, Machine) and cell.placed_entity.driving_speed == 0):
                    if cell.cell_id in self.positions_distance_matrix:
                        self.entity_fixed_assignment.append((cell.cell_id, cell.placed_entity.identification_str))

    def create_individual(self, available_positions: list[str], unassigned_stations: list[str]) -> list[tuple[str, str]]:
        if len(available_positions) < len(unassigned_stations):
            raise ValueError(f"Nicht genügend freie Positionen ({len(available_positions)}) für die nicht zugewiesenen Stationen ({len(unassigned_stations)}).")
        return list(zip(
            random.sample(available_positions, len(unassigned_stations)),
            random.sample(unassigned_stations, len(unassigned_stations))
        ))

    def run_genetic_loop(self):
        all_stations = [station for subdict in self.material_flow_matrix.values() for station in subdict.keys()]
        assigned_stations = [station for _, station in self.entity_fixed_assignment]
        unassigned_stations = list(set(all_stations) - set(assigned_stations))
        available_positions = list(set(self.positions_distance_matrix.keys()) - {pos for pos, _ in self.entity_fixed_assignment})

        try:
            population = [self.create_individual(available_positions, unassigned_stations) for _ in range(self.population_size)]
        except ValueError as e:
            raise ValueError(f"[ERROR] Fehler beim Erzeugen der Startpopulation: {e}")

        avg_performances = []
        best_performances = []
        std_devs = []

        for generation in range(self.number_of_iterations):
            performance_scores = []
            for ind in population:
                if self.is_valid_individual(ind):
                    performance_scores.append(self.calculate_performance(ind))
                else:
                    print(f"[WARN] Ungültiges Individuum in Generation {generation}: {ind}")
                    performance_scores.append(float('inf'))

            scored_population = list(zip(population, performance_scores))
            scored_population.sort(key=lambda x: x[1])

            avg = np.mean(performance_scores)
            std = np.std(performance_scores)

            avg_performances.append(avg)
            best_performances.append(scored_population[0][1])
            std_devs.append(std)

            survivors = [ind for ind, _ in scored_population[:self.number_of_surviving_parents]]
            next_generation = survivors[:]

            already_selected_for_tournament = set(tuple(map(tuple, survivors)))

            while len(next_generation) < self.population_size:
                parent1 = self.tournament_selection(scored_population, already_selected_for_tournament)
                already_selected_for_tournament.add(tuple(map(tuple, parent1)))

                parent2 = self.tournament_selection(scored_population, already_selected_for_tournament)
                already_selected_for_tournament.add(tuple(map(tuple, parent2)))

                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                next_generation.extend([child1, child2])

            population = next_generation[:self.population_size]

        best_individual = min(population, key=self.calculate_performance)
        self.entity_assignment = self.entity_fixed_assignment + best_individual

        self.plot_performance(avg_performances, best_performances, std_devs)
        self.save_performance_data(avg_performances, best_performances, std_devs)

    def is_valid_individual(self, individual: list[tuple[str, str]]) -> bool:
        position_dict = dict(self.entity_fixed_assignment + individual)
        all_entities = set(self.material_flow_matrix.keys()) | {dst for d in self.material_flow_matrix.values() for dst in d.keys()}

        if not all(entity in position_dict.values() for entity in all_entities):
            return False

        for src, dests in self.material_flow_matrix.items():
            for dst in dests:
                try:
                    inverse_position_dict = {v: k for k, v in position_dict.items()}
                    pos_src = inverse_position_dict[src]
                    pos_dst = inverse_position_dict[dst]
                    _ = self.positions_distance_matrix[pos_src][pos_dst]
                except KeyError:
                    return False
        return True

    def calculate_performance(self, individual: list[tuple[str, str]]) -> float:
        position_dict = dict(self.entity_fixed_assignment + individual)
        inverse_position_dict = {v: k for k, v in position_dict.items()}
        total_cost = 0.0
        skipped_pairs = 0
        missing_keys = set()

        for src, dest_dict in self.material_flow_matrix.items():
            for dst, quantity in dest_dict.items():
                try:
                    pos_src = inverse_position_dict[src]
                    pos_dst = inverse_position_dict[dst]
                    distance = self.positions_distance_matrix[pos_src][pos_dst]
                    total_cost += distance * quantity
                except KeyError:
                    skipped_pairs += 1
                    missing_keys.update([src, dst])

        if skipped_pairs > 0:
            print(f"[WARN] {skipped_pairs} Verbindungen konnten nicht berechnet werden. Ungültiges Individuum.")
            print(f"[DETAIL] Fehlende Stationen im position_dict: {sorted(missing_keys)}")
            return float('inf')

        return total_cost

    def tournament_selection(self, population_scores, already_selected):
        attempts = 0
        while attempts < 100:
            contenders = random.sample(population_scores, k=2)
            contenders.sort(key=lambda x: x[1])
            best = contenders[0][0]
            if tuple(map(tuple, best)) not in already_selected:
                return best
            attempts += 1
        return contenders[0][0]  # fallback

    def crossover(self, parent1, parent2):
        size = len(parent1)
        max_points = size - 1

        if self.points_of_separation > max_points:
            raise ValueError(f"Zu viele Trennpunkte: {self.points_of_separation} > {max_points}")
        points = sorted(random.sample(range(1, size), self.points_of_separation))

        toggle = False
        last = 0
        child1_raw = []
        child2_raw = []

        for point in points + [size]:
            segment1 = parent1[last:point]
            segment2 = parent2[last:point]

            if toggle:
                child1_raw.extend(segment2)
                child2_raw.extend(segment1)
            else:
                child1_raw.extend(segment1)
                child2_raw.extend(segment2)

            toggle = not toggle
            last = point

        child1_filtered, used_pos1, used_ent1 = self.filter_unique(child1_raw)
        child2_filtered, used_pos2, used_ent2 = self.filter_unique(child2_raw)

        all_positions = [pos for pos, _ in parent1]
        all_entities = [ent for _, ent in parent1]

        missing_pos1 = [pos for pos in all_positions if pos not in used_pos1]
        missing_ent1 = [ent for ent in all_entities if ent not in used_ent1]

        missing_pos2 = [pos for pos in all_positions if pos not in used_pos2]
        missing_ent2 = [ent for ent in all_entities if ent not in used_ent2]

        child1 = child1_filtered + list(zip(missing_pos1, missing_ent1))
        child2 = child2_filtered + list(zip(missing_pos2, missing_ent2))

        return child1, child2

    def filter_unique(self, pairs):
        seen_positions = set()
        seen_entities = set()
        filtered = []

        for pos, ent in pairs:
            if pos not in seen_positions and ent not in seen_entities:
                filtered.append((pos, ent))
                seen_positions.add(pos)
                seen_entities.add(ent)

        return filtered, seen_positions, seen_entities

    def mutate(self, individual):
        if random.randint(0, 100) < self.odds_of_mutation_per_genom_in_percent:
            idx1, idx2 = random.sample(range(len(individual)), 2)
            individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
        return individual

    def plot_performance(self, avg_performances, best_performances, std_devs):
        generations = range(len(avg_performances))
        avg_array = np.array(avg_performances)
        std_array = np.array(std_devs)

        plt.figure(figsize=(10, 6))
        plt.plot(generations, avg_array, label='Average Performance', color='blue')
        plt.fill_between(generations, avg_array - std_array, avg_array + std_array, color='blue', alpha=0.3, label='Standard Deviation')
        plt.plot(generations, best_performances, label='Best Performance', color='green')
        plt.xlabel('Generation')
        plt.ylabel('Performance')
        plt.title('Performance of Genetic Algorithm')
        plt.legend()
        filename = f"generation_plot_envnow_{self.env.now}.png"
        path = os.path.join(GENETIC_ALGORITHM, filename)
        plt.savefig(path)
        plt.close()

    def save_performance_data(self, avg_performances, best_performances, std_devs):
        data = [
            {
                "generation": i,
                "average_performance": avg,
                "best_performance": best,
                "std_deviation": std
            }
            for i, (avg, best, std) in enumerate(zip(avg_performances, best_performances, std_devs))
        ]

        filename = f"performance_data_envnow_{self.env.now}.json"
        path = os.path.join(GENETIC_ALGORITHM, filename)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
