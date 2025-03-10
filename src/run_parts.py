from src.command_line_service import CommandLineService
from src.data.coordinates import Coordinates
from src.data.production import Production
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.path_finding import PathFinding

# manufacturing_plan = ManufacturingPlan()
# manufacturing_plan.analyse_orders()


command_line_service = CommandLineService()
command_line_service.create_production()
path_finding = PathFinding()
path_finding.update_neighbors_for_complete_layout()
production = Production()
x = production.get_cell(Coordinates(0, 0))
y = production.get_cell(Coordinates(9,9))
funktioniert = path_finding.run_a_star_algorithm(x, y)
if funktioniert is True:
    print("Funktioniert")
else:
    print("Fehler")
command_line_service.visualise_layout()

