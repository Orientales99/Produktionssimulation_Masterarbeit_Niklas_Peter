from src.monitoring.data_analysis.convert_json_data import ConvertJsonData
from src.monitoring.data_analysis.visualize_machine_working_status import VisualizeMachineWorkingStatus
from src.monitoring.data_analysis.product_throughput import ProductThroughput
from src.monitoring.data_analysis.visualize_production_material_throughput import VisualizeProductionMaterialThroughput


def run_analysis():
    convert = ConvertJsonData()
    visualize_product_material_throughput = VisualizeProductionMaterialThroughput(convert)
    product_throughput = ProductThroughput(convert)

    visualize_product_material_throughput.plot_and_save_for_all_product_groups()
    visualize_product_material_throughput.plot_all_product_groups_with_legend()
    product_throughput.calculate_throughput_for_all_groups()


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
    machine_working_status = VisualizeMachineWorkingStatus(convert)
    machine_working_status.print()
#

if __name__ == '__main__':
    run_machine_working_status()

