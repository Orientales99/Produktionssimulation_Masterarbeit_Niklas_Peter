from src import SIMULATION_OUTPUT_DATA
from src.monitoring.data_analysis.convert_json_data import ConvertJsonData
from src.monitoring.data_analysis.creating_intermediate_store_during_simulation_dict import \
    CreatingIntermediateStoreDuringSimulationDict
from src.monitoring.data_analysis.creating_machine_during_simulation_dict import CreatingMachineDuringSimulationDict
from src.monitoring.data_analysis.creating_tr_during_simulation_dict import CreatingTrDuringSimulationDict
from src.monitoring.data_analysis.creating_wr_during_simulation_dict import CreatingWrDuringSimulationDict
from src.monitoring.data_analysis.machine_data.machine_processing_time import MachineProcessingTime
from src.monitoring.data_analysis.machine_data.machine_workload import MachineWorkload
from src.monitoring.data_analysis.product_throughput import ProductThroughput
from src.monitoring.data_analysis.transport_data.material_flow import MaterialFlow
from src.monitoring.data_analysis.transport_data.material_flow_heatmap import MaterialFlowHeatmap
from src.monitoring.data_analysis.transport_data.product_transporting_time import ProductTransportingTime
from src.monitoring.data_analysis.transport_data.tr_workload import TrWorkload
from src.monitoring.data_analysis.visualize_production_material_throughput import VisualizeProductionMaterialThroughput
from src.monitoring.data_analysis.wr_data.wr_workload import WrWorkload
from src.monitoring.deleting_data import DeletingData
from src.monitoring.simulation_data_saver import SimulationDataSaver
from src.production.production import Production
from src.provide_input_data.order_service import OrderService
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.simulation_environmnent.environment_simulation import EnvironmentSimulation


class CommandLineService:
    environment_simulation: EnvironmentSimulation

    def __init__(self):
        self.simulation_data_saver = SimulationDataSaver()
        self.order_service = OrderService()
        self.environment_simulation_test = EnvironmentSimulation(self.order_service)
        self.service_starting_conditions = StartingConditionsService()

        self.production = Production(self.environment_simulation_test.env, self.service_starting_conditions)

    def start_simulation(self):
        simulation_duration = self.production.service_starting_conditions.set_simulation_duration_per_day()
        print(f"Start_simulation: {simulation_duration}")

        self.environment_simulation = EnvironmentSimulation(self.order_service)
        self.environment_simulation.initialise_simulation_start()
        # self.environment_simulation.run_simulation(until=86400)
        self.environment_simulation.run_simulation(simulation_duration)
        self.start_analyse()

        self.secure_simulation_data(5)

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
        product_transporting_time = ProductTransportingTime(creating_tr_during_simulation_dict)
        product_transporting_time.calculate_transporting_time()

        # Analyse Workload of WR
        creating_wr_during_simulation_dict = CreatingWrDuringSimulationDict(convert)
        wr_workload = WrWorkload(creating_wr_during_simulation_dict)
        wr_workload.save_workload_statistics()

        # Analyse Workload of Machine
        machine_workload = MachineWorkload(creating_machine_during_simulation_dict)
        machine_workload.save_workload_statistics()

    def secure_simulation_data(self, experiment_number: int):
        self.simulation_data_saver.copy_folder(experiment_number)
