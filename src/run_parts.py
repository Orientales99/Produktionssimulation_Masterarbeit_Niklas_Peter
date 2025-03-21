import cProfile
from datetime import date

from src.command_line_service import CommandLineService
from src.data.coordinates import Coordinates
from src.data.production import Production
from src.data.service_product_information import ServiceProductInformation
from src.entity_classes.machine import Machine
from src.entity_classes.transport_robot import TransportRobot
from src.entity_classes.working_robot import WorkingRobot
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.path_finding import PathFinding
from src.process_logic.working_robot_manager import WorkingRobotManager


def run_pathfinding():
    command_line_service = CommandLineService()
    command_line_service.create_production()
    path_finding = PathFinding()
    production = Production()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    start_cell = production.get_cell(Coordinates(0, 24))
    end_cell = production.get_cell(Coordinates(23, 27))
    test_wr = WorkingRobot(1, Coordinates(4, 4), 1, 10)
    test_tr = TransportRobot(1, None, Coordinates(4, 4), 1, 10, 10)
    funktioniert = path_finding.run_a_star_algorithm(start_cell, end_cell, test_tr)
    path_finding.move_entity_along_path(start_cell, test_tr)

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
    # production.set_entities()
    command_line_service.visualise_layout()

    for x in range(0, 100):
        production.move_entity_right(WorkingRobot(1, Coordinates(2, 2), 1, 10))
    command_line_service.visualise_layout()

    for x in range(0, 3):
        production.move_entity_upwards(WorkingRobot(1, Coordinates(2, 2), 1, 10))
    command_line_service.visualise_layout()

    for x in range(0, 3):
        production.move_entity_right(WorkingRobot(1, Coordinates(2, 2), 1, 10))
    command_line_service.visualise_layout()

    for x in range(0, 100):
        production.move_entity_downwards(WorkingRobot(1, Coordinates(2, 2), 1, 10))
    command_line_service.visualise_layout()

    for x in range(0, 100):
        production.move_entity_left(WorkingRobot(1, Coordinates(2, 2), 1, 10))
    command_line_service.visualise_layout()

    for x in range(0, 100):
        production.move_entity_upwards(WorkingRobot(1, Coordinates(2, 2), 1, 10))
    command_line_service.visualise_layout()

    for x in range(0, 100):
        production.move_entity_downwards(WorkingRobot(1, Coordinates(2, 2), 1, 10))
    command_line_service.visualise_layout()

def run_manufacturing_plan():
    manufacturing_plan = ManufacturingPlan()
    command_line_service = CommandLineService()
    command_line_service.create_production()
    production = Production()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()


    manufacturing_plan.get_daily_manufacturing_plan(date(2024, 5, 2))
    manufacturing_plan.set_processing_machine_list__queue_length_estimation()
    manufacturing_plan.get_required_material_for_every_machine()
    command_line_service.visualise_layout()
    #working_robot_manager = WorkingRobotManager()
    # list_of_all_wr_identification_str = working_robot_manager.get_list_of_all_wr_identification_str()
    # working_robot_manager.get_every_process_order_from_machines()


if __name__ == '__main__':
    # move_entity()
    # run_pathfinding()
    # cProfile.run('run_pathfinding()')
    run_manufacturing_plan()
    #service_product_information = ServiceProductInformation()
    #service_product_information.create_product_information_list()
