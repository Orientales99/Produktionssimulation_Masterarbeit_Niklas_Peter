import cProfile

from src.command_line_service import CommandLineService
from src.data.coordinates import Coordinates
from src.data.production import Production
from src.entity_classes.working_robot import WorkingRobot
from src.process_logic.path_finding import PathFinding


# manufacturing_plan = ManufacturingPlan()
# manufacturing_plan.analyse_orders()

def run_pathfinding():
    command_line_service = CommandLineService()
    command_line_service.create_production()
    path_finding = PathFinding()
    production = Production()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    start_cell = production.get_cell(Coordinates(0, 24))
    end_cell = production.get_cell(Coordinates(33, 20))
    test_wr = WorkingRobot(1, Coordinates(3, 3), 1, 10)
    funktioniert = path_finding.run_a_star_algorithm(start_cell, end_cell, test_wr)
    path_finding.move_entity_along_path(start_cell, test_wr)

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


if __name__ == '__main__':
    # move_entity()
    #run_pathfinding()
    cProfile.run('run_pathfinding()')
