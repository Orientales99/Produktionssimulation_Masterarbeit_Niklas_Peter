import simpy

from src.process_logic.transport_robot.tr_order_manager import TrOrderManager
from src.production.production import Production
from src.production.visualisation.production_visualisation import ProductionVisualisation
from src.simulation_environmnent.simulation_control import SimulationControl


class VisualisationSimulation:
    def __init__(self, env: simpy.Environment, production: Production, tr_order_manager: TrOrderManager,
                 simulation_control: SimulationControl):
        self.env = env
        self.production = production
        self.tr_order_manager = tr_order_manager

        self.visualize_production = ProductionVisualisation(self.production, self.env, simulation_control)

    def visualize_layout(self):
        driving_speed = self.tr_order_manager.get_driving_speed_per_cell()
        yield self.env.timeout(29000)
        while True:
            self.visualize_production.visualize_layout()
            yield self.env.timeout(1 / driving_speed)
