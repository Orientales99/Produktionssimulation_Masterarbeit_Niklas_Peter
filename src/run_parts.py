from datetime import date

from src.command_line_service import CommandLineService
from src.production.base.coordinates import Coordinates
from src.entity.entity_working_status import EntityWorkingStatus
from src.production.entity_movement import EntityMovement
from src.production.production import Production
from src.entity.transport_robot import TransportRobot
from src.entity.working_robot import WorkingRobot
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.path_finding import PathFinding
from src.process_logic.working_robot_manager import WorkingRobotManager
from src.production.production_visualisation import ProductionVisualisation
from src.simulation_environmnent.simulation_environment import SimulationEnvironment


def run_pathfinding():
    command_line_service = CommandLineService()
    command_line_service.create_production()
    production = Production()
    path_finding = PathFinding(production)
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    start_cell = production.get_cell(Coordinates(0, 24))
    end_cell = production.get_cell(Coordinates(23, 27))
    test_wr = WorkingRobot(1, Coordinates(4, 4), 1, 10, EntityWorkingStatus())
    test_tr = TransportRobot(1, None, Coordinates(4, 4), 1, 10, 10)
    funktioniert = path_finding.run_a_star_algorithm(start_cell, end_cell, test_tr)
    path = path_finding.path_line_list
    path_finding.entity_movement.move_entity_one_step(start_cell, test_tr, path)

    if funktioniert is True:
        print("Funktioniert")
    else:
        print("Fehler")
    command_line_service.visualise_layout()


def run_1000():
    for x in range(0, 1000):
        run_pathfinding()


def move_entity():
    command_line_service = CommandLineService()
    command_line_service.create_production()
    production = Production()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    entity_movement = EntityMovement(production)
    # production.set_entities()
    command_line_service.visualise_layout()

    for x in range(0, 100):
        entity_movement.move_entity_right(WorkingRobot(1, Coordinates(2, 2), 1, 10, EntityWorkingStatus()))
    command_line_service.visualise_layout()

    for x in range(0, 3):
        entity_movement.move_entity_upwards(WorkingRobot(1, Coordinates(2, 2), 1, 10, EntityWorkingStatus()))
    command_line_service.visualise_layout()

    for x in range(0, 3):
        entity_movement.move_entity_right(WorkingRobot(1, Coordinates(2, 2), 1, 10, EntityWorkingStatus()))
    command_line_service.visualise_layout()

    for x in range(0, 100):
        entity_movement.move_entity_downwards(WorkingRobot(1, Coordinates(2, 2), 1, 10, EntityWorkingStatus()))
    command_line_service.visualise_layout()

    for x in range(0, 100):
        entity_movement.move_entity_left(WorkingRobot(1, Coordinates(2, 2), 1, 10, EntityWorkingStatus()))
    command_line_service.visualise_layout()

    for x in range(0, 100):
        entity_movement.move_entity_upwards(WorkingRobot(1, Coordinates(2, 2), 1, 10, EntityWorkingStatus()))
    command_line_service.visualise_layout()

    for x in range(0, 100):
        entity_movement.move_entity_downwards(WorkingRobot(1, Coordinates(2, 2), 1, 10, EntityWorkingStatus()))
    command_line_service.visualise_layout()


def run_manufacturing_plan():
    simulation_environment = SimulationEnvironment()
    command_line_service = CommandLineService()
    command_line_service.create_production()
    production = Production(simulation_environment)
    path_finding = PathFinding(production)
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    visualisation = ProductionVisualisation(production)

    manufacturing_plan = ManufacturingPlan(production)

    manufacturing_plan.get_daily_manufacturing_plan(date(2024, 5, 2))
    manufacturing_plan.set_processing_machine_list__queue_length_estimation()
    manufacturing_plan.get_required_material_for_every_machine()
    command_line_service.visualise_layout()
    working_robot_manager = WorkingRobotManager(manufacturing_plan, path_finding)
    working_robot_manager.start_working_robot_manager()
    visualisation.visualize_layout()

def run_simulation():
    command_line_service = CommandLineService()
    command_line_service.start_simulation()







if __name__ == '__main__':
    run_simulation()
    # move_entity()
    # run_pathfinding()
    # cProfile.run('run_pathfinding()')
    # run_manufacturing_plan()
    # service_product_information = ServiceProductInformation()
    # service_product_information.create_product_information_list()
