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
from src.monitoring.data_analysis.transport_data.tr_workload import TrWorkload
from src.monitoring.data_analysis.visualize_production_material_throughput import VisualizeProductionMaterialThroughput
from src.monitoring.data_analysis.wr_data.wr_workload import WrWorkload
from src.monitoring.deleting_data import DeletingData
from src.monitoring.simulation_data_saver import SimulationDataSaver
from src.rebuild_simulation.entities_specifc_simulation_time import EntitiesSpecificSimulationTime


def run_analysis():
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

    # Analyse Workload of WR
    creating_wr_during_simulation_dict = CreatingWrDuringSimulationDict(convert)
    wr_workload = WrWorkload(creating_wr_during_simulation_dict)
    wr_workload.save_workload_statistics()

    # Analyse Workload of Machine
    machine_workload = MachineWorkload(creating_machine_during_simulation_dict)
    machine_workload.save_workload_statistics()

def run_throughput_visualization():
    convert = ConvertJsonData(SIMULATION_OUTPUT_DATA)
    visualize_product_material_throughput = VisualizeProductionMaterialThroughput(convert)

    visualize_product_material_throughput.plot_and_save_for_all_product_groups()
    visualize_product_material_throughput.plot_all_product_groups_with_legend()


def run_throughput_stats():
    convert = ConvertJsonData(SIMULATION_OUTPUT_DATA)
    product_throughput = ProductThroughput(convert)

    product_throughput.calculate_throughput_for_all_groups()


def run_machine_working_status():
    convert = ConvertJsonData(SIMULATION_OUTPUT_DATA)
    creating_machine_during_simulation_dict = CreatingMachineDuringSimulationDict(convert)
    machine_processing_time = MachineProcessingTime(creating_machine_during_simulation_dict)
    # machine_processing_time.get_production_machine_data()


def run_tr_working_status():
    convert = ConvertJsonData(SIMULATION_OUTPUT_DATA)
    creating_tr_during_simulation_dict = CreatingTrDuringSimulationDict(convert)


def run_wr_working_status():
    convert = ConvertJsonData(SIMULATION_OUTPUT_DATA)
    creating_wr_during_simulation_dict = CreatingWrDuringSimulationDict(convert)

def run_copy_data():
    simulation_data_saver = SimulationDataSaver()
    simulation_data_saver.copy_folder(1)

if __name__ == '__main__':
    run_analysis()
    # run_machine_working_status()
    # run_tr_working_status()
    # run_wr_working_status()
    # run_copy_data()