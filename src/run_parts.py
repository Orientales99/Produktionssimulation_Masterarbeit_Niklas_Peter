import cProfile

from src.command_line_service import CommandLineService


def run_simulation():
    command_line_service = CommandLineService()
    command_line_service.start_simulation()


if __name__ == '__main__':
    run_simulation()
    # cProfile.run('run_simulation()')
