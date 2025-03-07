import pandas as pd

from collections import defaultdict

from src.data.coordinates import Coordinates

from src.data.order import Order
from src.data.product import Product
from src.data.service_order import ServiceOrder


class ManufacturingPlan:
    service_order = ServiceOrder()
    summarised_order_list: None
    df_summarised_order_per_day: pd.DataFrame

    def __init__(self):
        self.product_order_list = self.service_order.generate_order_list()

    def analyse_orders(self):
        self.summarise_orders()
        self.sort_list_by_date()
        print(self.df_summarised_order_per_day)

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
        self.df_summarised_order_per_day = {
            day: [order for order in self.summarised_order_list if order.order_date == day]
            for day in days}

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
