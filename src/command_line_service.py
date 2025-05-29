from src import SIMULATION_OUTPUT_DATA
from src.monitoring.data_analysis.convert_json_data import ConvertJsonData
from src.monitoring.data_analysis.creating_intermediate_store_during_simulation_dict import \
    CreatingIntermediateStoreDuringSimulationDict
from src.monitoring.data_analysis.creating_machine_during_simulation_dict import CreatingMachineDuringSimulationDict
from src.monitoring.data_analysis.creating_tr_during_simulation_dict import CreatingTrDuringSimulationDict
from src.monitoring.data_analysis.machine_data.machine_processing_time import MachineProcessingTime
from src.monitoring.data_analysis.product_throughput import ProductThroughput
from src.monitoring.data_analysis.transport_data.material_flow import MaterialFlow
from src.monitoring.data_analysis.transport_data.material_flow_heatmap import MaterialFlowHeatmap
from src.monitoring.data_analysis.transport_data.tr_workload import TrWorkload
from src.monitoring.data_analysis.visualize_production_material_throughput import VisualizeProductionMaterialThroughput
from src.monitoring.deleting_data import DeletingData
from src.monitoring.simulation_data_saver import SimulationDataSaver
from src.production.production import Production
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.simulation_environmnent.environment_simulation import EnvironmentSimulation


class CommandLineService:

    def __init__(self):
        self.simulation_data_saver = SimulationDataSaver()
        self.environment_simulation = EnvironmentSimulation()
        self.service_starting_conditions = StartingConditionsService()
        self.production = Production(self.environment_simulation, self.service_starting_conditions)

    def start_simulation(self):
        simulation_duration = self.production.service_starting_conditions.set_simulation_duration_per_day()
        number_of_simulation_runs = self.production.service_starting_conditions.get_number_of_simulation_runs()

        for simulation_run in range(number_of_simulation_runs):
            self.environment_testing_simulation = EnvironmentSimulation()

            self.environment_testing_simulation.initialise_simulation_start()
            # self.environment_simulation.run_simulation(until=86400)
            self.environment_testing_simulation.run_simulation(until=28800)

            self.start_analyse()

            self.secure_simulation_data(simulation_run)

    def start_analyse(self):
        deleting_data = DeletingData()
        deleting_data.delete_analysis_data()

        convert = ConvertJsonData(SIMULATION_OUTPUT_DATA)
        visualize_product_material_throughput = VisualizeProductionMaterialThroughput(convert)
        product_throughput = ProductThroughput(convert)
        creating_intermediate_store_during_simulation_dict = CreatingIntermediateStoreDuringSimulationDict(convert)

        # Analyse Throughput of Material in Production/ Machines
        visualize_product_material_throughput.plot_and_save_for_all_product_groups()
        visualize_product_material_throughput.plot_all_product_groups_with_legend()
        product_throughput.calculate_throughput_for_all_groups()

        # Analyse Machine Processing_time
        creating_machine_during_simulation_dict = CreatingMachineDuringSimulationDict(convert)
        machine_processing_time = MachineProcessingTime(creating_machine_during_simulation_dict)
        # Analyse Materialflow in a matrix
        creating_tr_during_simulation_dict = CreatingTrDuringSimulationDict(convert)
        material_flow = MaterialFlow(creating_tr_during_simulation_dict, creating_machine_during_simulation_dict,
                                     creating_intermediate_store_during_simulation_dict)
        material_flow.create_material_flow_matrix()
        # Analyse Materialflow with a heatmap
        material_flow_heatmap = MaterialFlowHeatmap(material_flow.object_material_flow_matrix)
        material_flow_heatmap.plot()
        # Analyse Workload of TR
        tr_workload = TrWorkload(creating_tr_during_simulation_dict)
        tr_workload.save_workload_statistics()

    def secure_simulation_data(self, experiment_number: int):
        self.simulation_data_saver.copy_folder(experiment_number)
