from dataclasses import dataclass


@dataclass
class SimulationControl:
    stop_event: bool
    stop_production_processes: bool

