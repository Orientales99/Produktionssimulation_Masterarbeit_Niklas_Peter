import pandas as pd


from src import RESOURCES, ANALYSIS_SOLUTION
from src.order_data.order import Order
from src.provide_input_data.product_information_service import ProductInformationService
from src.constant.constant import ProductGroup
from datetime import date


class OrderService:

    def __init__(self):
        self.df_order_list = None
        self.get_order_files_for_init()
        self.product_order_list = []
        self.service_product_information = ProductInformationService()
        self.service_product_information.create_product_information_list()

    def get_order_files_for_init(self):
        self.df_order_list = pd.read_excel(RESOURCES / 'Bestellauftraege.xlsx', header=None)

    def generate_order_list(self) -> list:
        self.remove_quotes_from_order_list()
        self.set_head_as_column_name()
        self.create_new_column_for_product_group()
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
        """Assigns a product group to the ordered product (from Constant ProductGroup)"""
        for group in ProductGroup:
            if value in group.building_groups_of_product():
                return group
        return None

    def set_product_order_list(self):
        """Creates an Order list that includes every order from the Excel sheet. """
        self.product_order_list = []

        for _, row in self.df_order_list.iterrows():
            product_group = row["product"]
            product = next((product for product in self.service_product_information.product_list if product.product_id == product_group), None)
            order = Order(
                product,
                row["AnzahlProArtikel"],
                date.fromisoformat(row["datum"]), 1
            )
            self.product_order_list.append(order)

    def print_as_xlsx(self):
        """printing the Order list in Excel"""
        self.df_order_list.to_excel(ANALYSIS_SOLUTION / 'bestellauftraege_auswertung.xlsx', sheet_name='Bestellauftraege',
                                    index=False)
