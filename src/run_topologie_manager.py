import simpy

from src.process_logic.machine.machine_execution import MachineExecution
from src.process_logic.machine.machine_manager import MachineManager
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.topologie_manager.object_material_flow_matrix import ObjectMaterialFlowMatrix
from src.process_logic.topologie_manager.positions_distance_matrix import PositionsDistanceMatrix
from src.production.production import Production
from src.production.store_manager import StoreManager
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
    current_date = production.service_starting_conditions.set_starting_date_of_simulation()
    store_manager = StoreManager(env)
    machine_manager = MachineManager(production, store_manager)
    manufacturing_plan = ManufacturingPlan(production, machine_manager)

    manufacturing_plan.set_parameter_for_start_of_a_simulation_day(current_date)

    material_flow_matrix = ObjectMaterialFlowMatrix(production, machine_manager)
    material_flow_matrix.start_creating_material_flow_matrix()

if __name__ == '__main__':
    # run_positions_distance_matrix()
    run_material_flow_matrix()
