class MachineProcessingTime:
    every_machine_during_simulation_data: dict[str, list(dict)]

    def __init__(self, creating_machine_during_simulation_dict):
        self.creating_machine_during_simulation_dict = creating_machine_during_simulation_dict
        self.every_machine_during_simulation_data = self.creating_machine_during_simulation_dict.every_machine_during_simulation_data

    def get_mean_processing_time(self) -> dict[str, int]: # dict[identification_str: str, mean: Durchlaufzeit, Standartabweichung: Durchlaufzeit, Varianz: Durchlaufzeit]
        pass
