import simpy

from src import SIMULATION_OUTPUT_DATA
from src.monitoring.data_analysis.convert_json_data import ConvertJsonData
from src.monitoring.data_analysis.creating_tr_during_simulation_dict import CreatingTrDuringSimulationDict
from src.monitoring.data_analysis.transport_data.material_flow import MaterialFlow
from src.monitoring.data_analysis.transport_data.material_flow_heatmap import MaterialFlowHeatmap
from src.process_logic.machine.machine_manager import MachineManager
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.topologie_manager.positions_distance_matrix import PositionsDistanceMatrix
from src.process_logic.topologie_manager.quadratic_assignment_problem import QuadraticAssignmentProblem
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
    convert = ConvertJsonData(SIMULATION_OUTPUT_DATA)

    # Analyse Materialflow in a matrix
    creating_tr_during_simulation_dict = CreatingTrDuringSimulationDict(convert)
    material_flow = MaterialFlow(creating_tr_during_simulation_dict)
    material_flow.create_material_flow_matrix()

    # Analyse Materialflow with a heatmap
    material_flow_heatmap = MaterialFlowHeatmap(material_flow.object_material_flow_matrix)
    material_flow_heatmap.plot()

def run_quadratic_assignment_problem():
    # distance matrix
    env = simpy.Environment()
    starting_condition = StartingConditionsService()

    production = Production(env, starting_condition)
    production.create_production()
    positions_distance_matrix = PositionsDistanceMatrix(production)

    # material flow matrix
    convert = ConvertJsonData(SIMULATION_OUTPUT_DATA)

    # Analyse Materialflow in a matrix
    creating_tr_during_simulation_dict = CreatingTrDuringSimulationDict(convert)
    material_flow = MaterialFlow(creating_tr_during_simulation_dict)

    # quadratic assignment problem
    quadratic_assignment_problem = QuadraticAssignmentProblem(material_flow, positions_distance_matrix)
    quadratic_assignment_problem.start_quadratic_assignment_problem()





if __name__ == '__main__':
    # run_positions_distance_matrix()
    # run_material_flow_matrix()
    run_quadratic_assignment_problem()
