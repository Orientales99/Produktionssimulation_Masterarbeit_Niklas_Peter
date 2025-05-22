import json

from src import RESOURCES


class GeneticAlgorithmService:
    def __init__(self):
        self.ga_information_list = {}

        self.get_ga_information_list()

    def get_ga_information_list(self):
        with open(RESOURCES / "genetic_algorithm_data.json", 'r', encoding='utf-8') as p:
            self.ga_information_list = json.load(p)

    def get_number_of_iterations(self) -> int:
        return self.ga_information_list["iterations"]

    def get_population_size_per_generation(self) -> int:
        return self.ga_information_list["population_per_generation"]

    def get_number_of_surviving_parents(self) -> int:
        return self.ga_information_list["surviving_parents"]

    def get_odds_of_mutation_per_genom_in_percent(self) -> int:
        return self.ga_information_list["odds_of_mutation_per_genom_in_percent"]

    def get_points_of_separation(self) -> int:
        return self.ga_information_list["points_of_separation"]
