from dataclasses import dataclass

from src.order_data.order import Order


@dataclass
class ProcessingOrder:
    order: Order
    step_of_the_process: int
    priority: int