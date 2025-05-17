import simpy

from src.process_logic.topologie_manager.object_material_flow_matrix import ObjectMaterialFlowMatrix
from src.process_logic.topologie_manager.positions_distance_matrix import PositionsDistanceMatrix
from src.production.production import Production
from src.provide_input_data.starting_condition_service import StartingConditionsService


def run_positions_distance_matrix():
    env = simpy.Environment()
    starting_condition = StartingConditionsService()

    production = Production(env, starting_condition)
    production.create_production()
    positions_distance_matrix = PositionsDistanceMatrix(production)
    positions_distance_matrix.start_creating_positions_distance_matrix()

def run_material_flow_matrix():
    env = simpy.Environment()
    starting_condition = StartingConditionsService()

    production = Production(env, starting_condition)
    production.create_production()
    material_flow_matrix = ObjectMaterialFlowMatrix(production)
    material_flow_matrix.start_creating_material_flow_matrix()

if __name__ == '__main__':
    # run_positions_distance_matrix()
    run_material_flow_matrix()
