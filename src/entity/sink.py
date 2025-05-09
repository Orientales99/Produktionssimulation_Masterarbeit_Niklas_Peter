from dataclasses import dataclass

from simpy import Store

from src.order_data.order import Order


@dataclass
class Sink:
    goods_issue_store: Store
    goods_issue_order_list: list[(Order, int)] # [Order, number_of_produced_items]

    @property
    def identification_str(self) -> str:
        return f"Sink"
