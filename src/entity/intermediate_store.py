from dataclasses import dataclass

from simpy import Store

from src.production.base.coordinates import Coordinates


@dataclass
class IntermediateStore:
    identification_number: int
    driving_speed: int
    size: Coordinates

    intermediate_store: Store

    @property
    def identification_str(self):
        return f"Intermediate Store: {self.identification_number}"
