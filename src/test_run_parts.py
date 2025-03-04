from src.command_line_service import CommandLineService
from src.data.order_service import OrderService
from src.data.production import Production

command_line_service = CommandLineService()
command_line_service.create_production()
production = Production()

production.get_flexible_machine_placed_in_production()
