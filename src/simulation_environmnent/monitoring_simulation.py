import simpy

from src.monitoring.SavingSimulationData import SavingSimulationData


class MonitoringSimulation:
    def __init__(self, env: simpy.Environment, saving_simulation_data: SavingSimulationData):
        self.env = env
        self.saving_simulation_data = saving_simulation_data

    def start_monitoring_process(self):
        self.saving_simulation_data.delete_every_json_file_in_anaylsis_solution()
        self.saving_simulation_data.delete_every_json_file_in_entities_during_simulation_data()
        self.saving_simulation_data.save_every_entity_identification_str()

        # save all entity Information at the beginning
        self.saving_simulation_data.save_one_cell_of_every_entity()
        self.saving_simulation_data.data_of_entities()

        # continuous saving the simulation data
        while True:
            self.saving_simulation_data.convert_simulating_machine_data_to_json()
            self.saving_simulation_data.convert_simulating_tr_data_to_json()
            self.saving_simulation_data.convert_simulating_wr_data_to_json()
            yield self.env.timeout(120)
