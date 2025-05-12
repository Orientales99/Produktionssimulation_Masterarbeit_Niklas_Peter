import simpy

from src.process_logic.transport_robot.tr_order_manager import TrOrderManager
from src.production.production import Production
from src.production.visualisation.production_visualisation import ProductionVisualisation


class VisualisationSimulation:
    def __init__(self, env: simpy.Environment, production: Production, tr_order_manager: TrOrderManager,
                 stop_event: bool):
        self.env = env
        self.production = production
        self.tr_order_manager = tr_order_manager
        self.stop_event = stop_event

        self.visualize_production = ProductionVisualisation(self.production, self.env)

    def visualize_layout(self):
        driving_speed = self.tr_order_manager.get_driving_speed_per_cell()
        while True:
            stop_event = self.visualize_production.visualize_layout()
            if stop_event is False:
                self.stop_event = False
            if stop_event is True:
                self.stop_event = True
            yield self.env.timeout(1 / driving_speed)

