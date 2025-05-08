from src.buck_fixing_command_line_service import BuckFixingCommandLineService


def debug_run():
    buck_fixing_command_line_service = BuckFixingCommandLineService()
    buck_fixing_command_line_service.start_simulation()

if __name__ == '__main__':
    debug_run()
