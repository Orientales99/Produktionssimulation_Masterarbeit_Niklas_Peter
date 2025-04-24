import json

import pandas as pd
import re
from pathlib import Path
from typing import Union

from src import SIMULATION_OUTPUT_DATA, ENTITIES_DURING_SIMULATION_DATA, MACHINES_DURING_SIMULATION_DATA, \
    TR_DURING_SIMULATION_DATA, WR_DURING_SIMULATION_DATA


class ConvertJsonData:
    entity_starting_data_df: pd.DataFrame
    goods_receipt_production_df: pd.DataFrame
    finished_products_leaving_production_df: pd.DataFrame
    combined_simulation_entity_data_df: pd.DataFrame

    def __init__(self):
        self.entity_starting_data_df = self.get_entity_data()
        self.goods_receipt_production_df = self.get_df_goods_entering_production()
        self.finished_products_leaving_production_df = self.get_df_finished_products_leaving_production()
        self.simulation_machine_data_df = self.get_machine_simulation_df()
        self.simulation_tr_data_df = self.get_tr_simulation_df()
        self.simulation_wr_data_df = self.get_wr_simulation_df()

    def get_entity_data(self) -> pd.DataFrame:
        """Create a df with all entities and their starting stats"""
        with open(ENTITIES_DURING_SIMULATION_DATA / "entity_starting_data.json", 'r',
                  encoding='utf-8') as entity_data:
            data = json.load(entity_data)
            return pd.DataFrame(data)

    def get_df_goods_entering_production(self) -> pd.DataFrame:
        """Create a df with all the products entering the production and the time"""

        with open(SIMULATION_OUTPUT_DATA / "data_goods_entering_production.json", 'r',
                  encoding='utf-8') as receipt_products:
            data = json.load(receipt_products)
            return pd.DataFrame(data)

    def get_df_finished_products_leaving_production(self) -> pd.DataFrame:
        """Create a df with all the products leaving the production and the time"""

        with open(SIMULATION_OUTPUT_DATA / "data_finished_products_leaving_production.json", 'r',
                  encoding='utf-8') as finished_products:
            data = json.load(finished_products)
            return pd.DataFrame(data)

    def get_machine_simulation_df(folder_path: Union[str, Path]) -> pd.DataFrame:

        folder = Path(MACHINES_DURING_SIMULATION_DATA)
        pattern = re.compile(r"simulation_machine_run_data_from_(\d+)_sec_to_(\d+)_sec\.json")

        all_data = []
        file_info = []

        # Collect files and extract start time
        for file in folder.glob("simulation_machine_run_data_from_*_sec_to_*_sec.json"):
            match = pattern.match(file.name)
            if match:
                start_time = int(match.group(1))
                file_info.append((start_time, file))

        # Sort by start time
        file_info.sort(key=lambda x: x[0])

        # Read in all JSONs and collect them in a list
        for _, file in file_info:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_data.extend(data)

        return pd.DataFrame(all_data)

    def get_tr_simulation_df(folder_path: Union[str, Path]) -> pd.DataFrame:

        folder = Path(TR_DURING_SIMULATION_DATA)
        pattern = re.compile(r"simulation_tr_run_data_from_(\d+)_sec_to_(\d+)_sec\.json")

        all_data = []
        file_info = []

        # Collect files and extract start time
        for file in folder.glob("simulation_tr_run_data_from_*_sec_to_*_sec.json"):
            match = pattern.match(file.name)
            if match:
                start_time = int(match.group(1))
                file_info.append((start_time, file))

        # Sort by start time
        file_info.sort(key=lambda x: x[0])

        # Read in all JSONs and collect them in a list
        for _, file in file_info:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_data.extend(data)

        return pd.DataFrame(all_data)

    def get_wr_simulation_df(folder_path: Union[str, Path]) -> pd.DataFrame:

        folder = Path(WR_DURING_SIMULATION_DATA)
        pattern = re.compile(r"simulation_wr_run_data_from_(\d+)_sec_to_(\d+)_sec\.json")

        all_data = []
        file_info = []

        # Collect files and extract start time
        for file in folder.glob("simulation_wr_run_data_from_*_sec_to_*_sec.json"):
            match = pattern.match(file.name)
            if match:
                start_time = int(match.group(1))
                file_info.append((start_time, file))

        # Sort by start time
        file_info.sort(key=lambda x: x[0])

        # Read in all JSONs and collect them in a list
        for _, file in file_info:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_data.extend(data)

        return pd.DataFrame(all_data)
