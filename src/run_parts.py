import cProfile

from src.command_line_service import CommandLineService
from src.data.coordinates import Coordinates
from src.data.production import Production
from src.entity_classes.working_robot import WorkingRobot
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.path_finding import PathFinding


# manufacturing_plan = ManufacturingPlan()
# manufacturing_plan.analyse_orders()

def run_pathfinding():
    command_line_service = CommandLineService()
    command_line_service.create_production()
    path_finding = PathFinding()
    production = Production()
    x = production.get_cell(Coordinates(0, 0))
    y = production.get_cell(Coordinates(9, 9))
    funktioniert = path_finding.run_a_star_algorithm(x, y)
    if funktioniert is True:
        print("Funktioniert")
    else:
        print("Fehler")
    command_line_service.visualise_layout()


def run_1000():
    for x in range(0, 1000):
        run_pathfinding()


def init_production():
    command_line_service = CommandLineService()
    command_line_service.create_production()
    production = Production()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    production.set_entities()
    command_line_service.visualise_layout()
    for x in range(0, 35):
        production.move_entity_right(WorkingRobot(1, Coordinates(1, 1), 1, 10))
        command_line_service.visualise_layout()

    for x in range(0, 12):
        production.move_entity_downwards(WorkingRobot(1, Coordinates(1, 1), 1, 10))
        command_line_service.visualise_layout()

   # for x in range(0, 3):
   #     production.move_entity_left(WorkingRobot(1, Coordinates(1, 1), 1, 10))
   #     command_line_service.visualise_layout()
#
   # for x in range(0,10):
   #     production.move_entity_upwards(WorkingRobot(1, Coordinates(1, 1), 1, 10))
   #     command_line_service.visualise_layout()


    # for value in production.entities_located.values():
    #    print(production.entities_located.keys())
    #    print("\n")
    #    print(value)
    # print("\n")


if __name__ == '__main__':
    init_production()

    #cProfile.run('init_production()')
