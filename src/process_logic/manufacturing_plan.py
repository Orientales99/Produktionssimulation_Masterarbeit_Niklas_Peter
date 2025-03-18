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
        print(self.daily_manufacturing_plan)

    def analyse_orders(self):
        self.summarise_orders()
        self.sort_list_by_date()

    def summarise_orders(self):
        """Groups identical product orders on every day and calculates their total quantity.
        list summarised_order_list = Order[Product, count(how often the product was ordered), order_date, priority) """
        order_count = defaultdict(int)

        for order in self.product_order_list:
            order_for_summarise = (
                order.product.product_id,
                order.order_date,
                order.priority
            )
            order_count[order_for_summarise] += int(order.number_of_products_per_order)

        print("Keys in order_count:", list(order_count.keys()))  # Debugging-Ausgabe

        self.summarised_order_list = []
        for (product_id, order_date, priority), count in order_count.items():
            product = next(
                (product for product in self.service_product_information.product_list
                 if product.product_id == product_id), None
            )

            if product is None:
                raise ValueError(f"Produkt mit product_id {product_id} wurde nicht gefunden.")

            # Bestellungen zusammenfassen
            self.summarised_order_list.append(
                Order(
                    product,
                    count,
                    order_date,
                    priority
                )
            )

    def sort_list_by_date(self):
        """sorts the list summarised_order_list by day, the day furthest in the past is placed first on the list"""
        period_of_time = self.range_of_days()
        days = pd.date_range(period_of_time[0], period_of_time[1], freq="D").date
        self.dictionary_summarised_order_per_day = self.dictionary_summarised_order_per_day = {
            day: {"date": day, "orders": [order for order in self.summarised_order_list if order.order_date == day]}
            for day in days
        }

    def range_of_days(self) -> tuple:
        """creating a tuple (first date, last date) in the range of every order that was taken"""
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
        """creating a list of every order for one specific date (list: daily_manufacturing_plan)"""
        orders_for_day = self.dictionary_summarised_order_per_day.get(date, {}).get("orders", [])

        sorted_orders = sorted(orders_for_day, key=lambda order: order.number_of_products_per_order, reverse=True)

        for sequence, order in enumerate(sorted_orders):
            order.daily_manufacturing_sequence = sequence

        self.daily_manufacturing_plan = sorted_orders
