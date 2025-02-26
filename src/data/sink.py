from dataclasses import dataclass


@dataclass
class Sink:
    number_of_static_wr: int
    number_of_tr: int
    product_transfer_rate: int
