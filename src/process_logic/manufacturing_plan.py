import pandas as pd

from collections import defaultdict

from src.data.coordinates import Coordinates

from src.data.order import Order
from src.data.product import Product
from src.data.service_order import ServiceOrder
from src.data.service_product_information import ServiceProductInformation


class ManufacturingPlan:
    service_order = ServiceOrder()
    service_product_information = ServiceProductInformation()
    summarised_order_list: list[Order] | None
    dictionary_summarised_order_per_day: dict = {}
    daily_manufacturing_plan: list[Order] = []

    def __init__(self):
        self.product_order_list = self.service_order.generate_order_list()
        self.product_information_list = self.service_product_information.create_product_information_list()

    def get_daily_manufacturing_plan(self, date):
        self.analyse_orders()
        self.manufacturing_sequence_per_day(date)
        print("Hallo")
        print(self.daily_manufacturing_plan)

    def analyse_orders(self):
        self.summarise_orders()
        self.sort_list_by_date()
        print(self.dictionary_summarised_order_per_day)

    def summarise_orders(self):
        order_count = defaultdict(int)

        for order in self.product_order_list:
            order_for_summarise = (
                order.product.product_id,
                order.product.size.x,
                order.product.size.y,
                order.product.item_type,
                order.order_date,
                order.priority
            )
            order_count[order_for_summarise] += int(order.number_of_products_per_order)

        self.summarised_order_list = [
            Order(
                Product(
                    product_id,
                    Coordinates(x, y),
                    item_type),
                count,
                order_date,
                priority
            )
            for (product_id, x, y, item_type, order_date, priority), count in order_count.items()]

    def sort_list_by_date(self):
        period_of_time = self.range_of_days()
        days = pd.date_range(period_of_time[0], period_of_time[1], freq="D").date
        df_summarised_order_list = self.summarised_order_list
        self.dictionary_summarised_order_per_day = self.dictionary_summarised_order_per_day = {
            day: {"date": day, "orders": [order for order in self.summarised_order_list if order.order_date == day]}
            for day in days
            }

    def range_of_days(self) -> tuple:
        first_date = None
        last_date = None
        for order in self.summarised_order_list:
            if first_date is None or order.order_date < first_date:
                first_date = order.order_date
            if last_date is None or order.order_date > last_date:
                last_date = order.order_date
        period_of_time = (first_date, last_date)
        return period_of_time

    def manufacturing_sequence_per_day(self, date):
        orders_for_day = self.dictionary_summarised_order_per_day.get(date, {}).get("orders", [])

        sorted_orders = sorted(orders_for_day, key=lambda order: order.number_of_products_per_order, reverse=True)

        for sequence, order in enumerate(sorted_orders):
            order.daily_manufacturing_sequence = sequence

        self.daily_manufacturing_plan = sorted_orders



