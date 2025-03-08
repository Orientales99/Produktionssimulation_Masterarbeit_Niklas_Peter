from src.command_line_service import CommandLineService
from src.data.coordinates import Coordinates
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.path_finding import PathFinding

# manufacturing_plan = ManufacturingPlan()
# manufacturing_plan.analyse_orders()


command_line_service = CommandLineService()
command_line_service.create_production()
path_finding = PathFinding()
path_finding.update_cell_neighbors_list(Coordinates(15, 52))
command_line_service.visualise_layout()

