import pandas as pd

from src import RESOURCES
from src.data.coordinates import Coordinates
from src.data.order import Order
from src.data.product import Product
from src.data.simulation_environment import SimulationEnvironment
from src.data.constant import ProductGroup, ItemType
from datetime import date


class ServiceOrder:

    def __init__(self):
        self.df_order_list = None
        self.env = SimulationEnvironment()
        self.get_order_files_for_init()
        self.product_order_list = []

    def get_order_files_for_init(self):
        self.df_order_list = pd.read_excel(RESOURCES / 'Bestellauftraege.xlsx', header=None)

    def generate_order_list(self) -> list:
        self.remove_quotes_from_order_list()
        self.set_head_as_column_name()
        self.create_new_column_for_product_group()
        print(self.df_order_list)
        self.set_product_order_list()
        return self.product_order_list

    def remove_quotes_from_order_list(self):
        self.df_order_list = self.df_order_list.apply(lambda x: x.str.replace('"', ''))

    def set_head_as_column_name(self):
        """delete first row, split row in separate_columns, set deleted row as head"""
        header = self.df_order_list.iloc[0, 0].split(',')
        self.df_order_list = self.df_order_list.drop(0).reset_index(drop=True)
        self.split_row_in_separate_columns()
        self.df_order_list.columns = header

    def split_row_in_separate_columns(self):
        self.df_order_list = self.df_order_list[0].str.split(',', expand=True)

    def create_new_column_for_product_group(self):
        self.df_order_list["product"] = self.df_order_list["sku"].apply(self.get_product_group)

    def get_product_group(self, value: str) -> ProductGroup:
        for group in ProductGroup:
            if value in group.building_groups_of_product():
                return group
        return None

    def set_product_order_list(self):
        self.product_order_list = []

        for _, row in self.df_order_list.iterrows():
            order = Order(
                Product(
                    ProductGroup(row["product"]),
                    Coordinates(0, 0),
                    ItemType.FINAL_PRODUCT_PACKED),
                row["AnzahlProArtikel"],
                date.fromisoformat(row["datum"]), 1
            )
            self.product_order_list.append(order)

    def print_as_xlsx(self):
        self.df_order_list.to_excel(RESOURCES / 'bestellauftraege_auswertung.xlsx', sheet_name='Bestellauftraege',
                                    index=False)
