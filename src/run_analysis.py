from src.monitoring.data_analysis.convert_json_data import ConvertJsonData
from src.monitoring.data_analysis.creating_intermediate_store_during_simulation_dict import \
    CreatingIntermediateStoreDuringSimulationDict
from src.monitoring.data_analysis.creating_machine_during_simulation_dict import CreatingMachineDuringSimulationDict
from src.monitoring.data_analysis.creating_tr_during_simulation_dict import CreatingTrDuringSimulationDict
from src.monitoring.data_analysis.creating_wr_during_simulation_dict import CreatingWrDuringSimulationDict
from src.monitoring.data_analysis.machine_data.machine_processing_time import MachineProcessingTime
from src.monitoring.data_analysis.product_throughput import ProductThroughput
from src.monitoring.data_analysis.production_topology.production_topology import ProductionTopology
from src.monitoring.data_analysis.transport_data.material_flow import MaterialFlow
from src.monitoring.data_analysis.transport_data.material_flow_heatmap import MaterialFlowHeatmap
from src.monitoring.data_analysis.transport_data.tr_workload import TrWorkload
from src.monitoring.data_analysis.visualize_production_material_throughput import VisualizeProductionMaterialThroughput
from src.rebuild_simulation.entities_specifc_simulation_time import EntitiesSpecificSimulationTime


def run_analysis():
    convert = ConvertJsonData()
    visualize_product_material_throughput = VisualizeProductionMaterialThroughput(convert)
    product_throughput = ProductThroughput(convert)
    creating_intermediate_store_during_simulation_dict = CreatingIntermediateStoreDuringSimulationDict(convert)

    # Analyse Throughput of Material in Production/ Machines
    visualize_product_material_throughput.plot_and_save_for_all_product_groups()
    visualize_product_material_throughput.plot_all_product_groups_with_legend()
    product_throughput.calculate_throughput_for_all_groups()
#
    # # Analyse Machine Processing_time
    creating_machine_during_simulation_dict = CreatingMachineDuringSimulationDict(convert)
    machine_processing_time = MachineProcessingTime(creating_machine_during_simulation_dict)

    # Analyse Materialflow in a matrix
    creating_tr_during_simulation_dict = CreatingTrDuringSimulationDict(convert)
    material_flow = MaterialFlow(creating_tr_during_simulation_dict, creating_machine_during_simulation_dict, creating_intermediate_store_during_simulation_dict)
    material_flow.create_material_flow_matrix()

    # Analyse Materialflow with a heatmap
    material_flow_heatmap = MaterialFlowHeatmap(material_flow.object_material_flow_matrix)
    material_flow_heatmap.plot()

    # Analyse Workload of TR
    tr_workload = TrWorkload(creating_tr_during_simulation_dict)
    tr_workload.save_workload_statistics()



def run_throughput_visualization():
    convert = ConvertJsonData()
    visualize_product_material_throughput = VisualizeProductionMaterialThroughput(convert)

    visualize_product_material_throughput.plot_and_save_for_all_product_groups()
    visualize_product_material_throughput.plot_all_product_groups_with_legend()


def run_throughput_stats():
    convert = ConvertJsonData()
    product_throughput = ProductThroughput(convert)

    product_throughput.calculate_throughput_for_all_groups()


def run_machine_working_status():
    convert = ConvertJsonData()
    creating_machine_during_simulation_dict = CreatingMachineDuringSimulationDict(convert)
    machine_processing_time = MachineProcessingTime(creating_machine_during_simulation_dict)
    # machine_processing_time.get_production_machine_data()


def run_tr_working_status():
    convert = ConvertJsonData()
    creating_tr_during_simulation_dict = CreatingTrDuringSimulationDict(convert)


def run_wr_working_status():
    convert = ConvertJsonData()
    creating_wr_during_simulation_dict = CreatingWrDuringSimulationDict(convert)


if __name__ == '__main__':
    run_analysis()
    # run_machine_working_status()
    # run_tr_working_status()
    # run_wr_working_status()
