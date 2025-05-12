from src.rebuilding_command_line_service import RebuildingCommandLineService


def debug_run():
    buck_fixing_command_line_service = RebuildingCommandLineService()
    buck_fixing_command_line_service.start_simulation()

if __name__ == '__main__':
    debug_run()
