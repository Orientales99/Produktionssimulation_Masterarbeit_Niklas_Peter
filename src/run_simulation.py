from src.simulation_starter import SimulationStarter


def run_simulation():
    command_line_service = SimulationStarter()
    command_line_service.start_simulation()
    command_line_service.start_analyse()
    command_line_service.secure_simulation_data(1)


if __name__ == '__main__':
    run_simulation()
