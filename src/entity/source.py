from dataclasses import dataclass

from src.order_data.order import Order


@dataclass
class Source:
    number_of_static_wr: int
    number_of_tr: int
    product_transfer_rate: int

    @property
    def identification_str(self) -> str:
        return f"Source"
