from dataclasses import dataclass

from src.data.product import Product
from src.data.constant import OrderPriority
from datetime import date


@dataclass
class Order:
    product: Product
    number_of_products_per_order: int
    order_date: date
    priority: OrderPriority


