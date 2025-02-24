from src.data.product import Product
from src.data.constant import OrderPriority


class Order:
    product: Product
    number_of_orders_per_product: int
    priority: OrderPriority

    def __init__(self, product, number_of_orders_per_product, priority):
        self.product = product
        self.number_of_orders_per_product = number_of_orders_per_product
        self.priority = priority
