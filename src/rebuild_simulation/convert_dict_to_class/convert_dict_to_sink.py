from datetime import date

import simpy
from simpy import Store

from src.constant.constant import ProductGroup, ItemType, OrderPriority
from src.entity.sink import Sink
from src.order_data.order import Order
from src.order_data.product import Product
from src.order_data.production_material import ProductionMaterial
from src.production.base.coordinates import Coordinates
from src.provide_input_data.product_information_service import ProductInformationService


class ConvertDictToSink:
    def __init__(self, env: simpy.Environment):
        self.env = env

        self.product_information_service = ProductInformationService()
        self.product_information_list = self.product_information_service.create_product_information_list()

    def deserialize_complete_sink(self, sink_dict: dict) -> Sink:
        goods_issue_store = self.get_goods_issue_store(sink_dict[0]["entities"][0]["entity_data"]["goods_issue_store"])

        goods_issue_order_list = self.goods_issue_order_list(
            sink_dict[0]["entities"][0]["entity_data"]["goods_issue_order_list"])

        return Sink(
            goods_issue_store=goods_issue_store,
            goods_issue_order_list=goods_issue_order_list
        )

    def get_goods_issue_store(self, store_dict: dict) -> Store:
        contained_units = store_dict["Contained Units"]
        max_store_capacity = store_dict["Max Capacity"]
        if max_store_capacity == "Infinity":
            max_store_capacity = float("inf")

        if contained_units != 0:
            for identification_str in store_dict["Loaded Products"]:
                production_material = self._rebuild_production_material_from_ident_str(identification_str)
                store = Store(self.env, capacity=max_store_capacity)
                for _ in range(contained_units):
                    store.items.append(production_material)
        else:
            store = Store(self.env, capacity=max_store_capacity)
        return store

    def _rebuild_production_material_from_ident_str(self, ident_str: str) -> ProductionMaterial | None:
        """
        Rebuilds a ProductionMaterial object from its identification string.
        Extracts information like ProductGroup, ItemType, and Size.
        """
        # Example of how to split the identification string
        parts = ident_str.split(".")

        product_group = ProductGroup[parts[1]]  # z.B. 'FIFTEEN' → ProductGroup.FIFTEEN
        item_type = int(parts[2])

        try:
            # Convert the ProductGroup to the enum
            production_material_id = product_group
        except KeyError:
            raise ValueError(f"Invalid ProductGroup in identification string: {product_group}")

        try:
            # Convert the ItemType to the enum
            item_type = ItemType(item_type)
        except ValueError:
            raise ValueError(f"Invalid ItemType in identification string: {item_type}")

        # Assuming a fixed size (or it could be part of the identification string if needed)
        size = Coordinates(x=1, y=1)  # Example size; adjust if necessary

        return ProductionMaterial(
            identification_str=ident_str,
            production_material_id=production_material_id,
            size=size,
            item_type=item_type
        )

    def goods_issue_order_list(self, goods_issue_order_list_dict: list[dict]) -> list[(Order, int)]:
        goods_issue_order_list = []

        for order_dict in goods_issue_order_list_dict:
            order = self._rebuild_order(order_dict)
            number_of_produced_items = order_dict["number_of_produced_items"]
            goods_issue_order_list.append((order,number_of_produced_items))

        return goods_issue_order_list

    def _rebuild_order(self, order_dict: dict) -> Order:
        """
        Rebuilds an Order object from a dictionary, properly handling all complex attributes
        like Product, OrderPriority, and the attributes related to production steps.
        """
        # Extracting basic information for Order
        product_data = order_dict["product_identification"]
        product_data = product_data.split(" ", 1)[1]
        product = self._rebuild_product(product_data)

        order_date = order_dict["order_date"]
        if isinstance(order_date, str):
            order_date = self._parse_date(order_date)  # Assuming this method parses the date string to a date object

        priority_str = order_dict["priority"]
        priority = OrderPriority[priority_str]

        daily_manufacturing_sequence = order_dict["daily_manufacturing_sequence"]

        return Order(
            product=product,
            number_of_products_per_order=order_dict.get("number_of_products_per_order", 0),
            order_date=order_date,
            priority=priority,
            daily_manufacturing_sequence=daily_manufacturing_sequence
        )

    def _rebuild_product(self, product_id: str) -> Product:
        """
        Rebuilds the Product object from a pro.
        """
        for product in self.product_information_list:
            if str(product.product_id) == product_id:
                return product

    def _parse_date(self, date_str: str) -> date:
        """
        Helper method to parse date strings into actual date objects.
        """
        from datetime import datetime
        return datetime.strptime(date_str, "%Y-%m-%d").date()
