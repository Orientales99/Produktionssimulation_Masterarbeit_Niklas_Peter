from src.monitoring.data_analysis.convert_json_data import ConvertJsonData


def test_get_df_goods_entering_production():
    convert_json = ConvertJsonData()
    convert_json.get_df_goods_entering_production()
