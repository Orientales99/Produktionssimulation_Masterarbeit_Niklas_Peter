from dataclasses import dataclass

from simpy import Store


@dataclass
class Sink:
    number_of_static_wr: int
    number_of_tr: int
    product_transfer_rate: int

    goods_issue_store: Store

    def identification_str(self) -> str:
        return f"Sink"