from dataclasses import dataclass

from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.order_data.production_material import ProductionMaterial


@dataclass
class TransportOrder:
    unload_destination: Machine | Sink | Source
    pick_up_station: Machine | Source
    transporting_product: ProductionMaterial
    quantity: int
