from src.simulation_starter import SimulationStarter
import cProfile


def main():
    command_line_service = SimulationStarter()
    command_line_service.create_production()
    command_line_service.visualise_layout()

def check_performance():
    cProfile.run('main()')

if __name__ == '__main__':
    main()
