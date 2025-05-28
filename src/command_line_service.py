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
from src.production.production import Production
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.simulation_environmnent.environment_simulation import EnvironmentSimulation


class CommandLineService:
    environment_simulation = EnvironmentSimulation()

    service_starting_conditions = StartingConditionsService()
    production = Production(environment_simulation, service_starting_conditions)

    def start_simulation(self):
        simulation_duration = self.production.service_starting_conditions.set_simulation_duration_per_day()
        self.environment_simulation.initialise_simulation_start()
        self.environment_simulation.run_simulation(until=86400)
        self.start_analyse()

    def start_analyse(self):
        convert = ConvertJsonData()
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
