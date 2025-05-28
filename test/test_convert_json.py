from src import SIMULATION_OUTPUT_DATA
from src.monitoring.data_analysis.convert_json_data import ConvertJsonData


def test_get_df_goods_entering_production():
    convert_json = ConvertJsonData(SIMULATION_OUTPUT_DATA)
    convert_json.get_df_goods_entering_production()
