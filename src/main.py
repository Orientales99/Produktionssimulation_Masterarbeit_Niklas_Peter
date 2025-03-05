from src.command_line_service import CommandLineService
from src.data.order_service import OrderService

if __name__ == '__main__':
    command_line_service = CommandLineService()
    command_line_service.create_production()

    #  command_line_service.get_cell_information()
