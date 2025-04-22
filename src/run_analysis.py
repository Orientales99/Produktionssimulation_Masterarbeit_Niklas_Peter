from src.monitoring.data_analysis.convert_json_data import ConvertJsonData
from src.monitoring.data_analysis.analysis_production_material import AnalysisProductionMaterial


def run_analysis():
    convert = ConvertJsonData()
    analysis_production_material = AnalysisProductionMaterial(convert)

    analysis_production_material.plot_and_save_for_all_product_groups()
    analysis_production_material.plot_all_product_groups_with_legend()


if __name__ == '__main__':
    run_analysis()
