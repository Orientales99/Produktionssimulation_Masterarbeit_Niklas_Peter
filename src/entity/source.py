from dataclasses import dataclass


@dataclass
class Source:
    number_of_static_wr: int
    number_of_tr: int
    product_transfer_rate: int

    @property
    def identification_str(self) -> str:
        return f"Source"
