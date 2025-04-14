from dataclasses import dataclass

from src.entity.Process_material import ProcessMaterial
from src.entity.machine import Machine
from src.entity.processing_order import ProcessingOrder
from src.entity.sink import Sink
from src.entity.source import Source


@dataclass
class TransportRequest:
    destination_pick_up: Machine | Source
    destination_unload: Machine | Sink
    processing_order: ProcessingOrder
    process_material: ProcessMaterial