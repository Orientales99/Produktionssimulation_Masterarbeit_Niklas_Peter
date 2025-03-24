from dataclasses import dataclass

from src.gruppe_eins.product import Product
from src.constant.constant import OrderPriority
from datetime import date


@dataclass
class Order:
    product: Product
    number_of_products_per_order: int
    order_date: date
    priority: OrderPriority
    daily_manufacturing_sequence: int | None = None

