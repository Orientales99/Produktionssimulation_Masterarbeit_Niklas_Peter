from src.command_line_service import CommandLineService
from src.data.service_order import ServiceOrder
import cProfile


def main():
    command_line_service = CommandLineService()
    command_line_service.create_production()
    command_line_service.visualise_layout()

def check_performance():
    cProfile.run('main()')

if __name__ == '__main__':
    main()
