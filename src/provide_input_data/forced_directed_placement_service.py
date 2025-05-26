import json

from src import RESOURCES


class ForcedDirectedPlacementService:
    def __init__(self):
        self.fdp_information_list = {}

        self.get_fdp_information_list()

    def get_fdp_information_list(self):
        with open(RESOURCES / "forced_directed_placement_data.json", 'r', encoding='utf-8') as p:
            self.fdp_information_list = json.load(p)

    def get_number_of_iterations(self) -> int:
        return self.fdp_information_list["iterations"]

    def get_k(self) -> float:
        return self.fdp_information_list["k"]
