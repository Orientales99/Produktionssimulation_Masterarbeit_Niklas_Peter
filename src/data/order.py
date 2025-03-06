from src.data.product import Product
from src.data.constant import OrderPriority
from datetime import date


class Order:
    product: Product
    number_of_products_per_order: int
    order_date: date
    priority: OrderPriority

    def __init__(self, product, number_of_products_per_order, order_date, priority):
        self.product = product
        self.number_of_products_per_order = number_of_products_per_order
        self.order_date = order_date
        self.priority = priority
