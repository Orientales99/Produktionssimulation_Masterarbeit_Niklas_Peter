from src.command_line_service import CommandLineService
from src.data.service_order import ServiceOrder

if __name__ == '__main__':
    command_line_service = CommandLineService()
    command_line_service.create_production()
    command_line_service.visualise_layout()
