from dataclasses import dataclass

from simpy import Store

from src.order_data.order import Order


@dataclass
class Sink:
    number_of_static_wr: int
    number_of_tr: int
    product_transfer_rate: int

    goods_issue_store: Store
    goods_issue_order_list: list[(Order, int)] # [Order, number_of_produced_items]

    def identification_str(self) -> str:
        return f"Sink"