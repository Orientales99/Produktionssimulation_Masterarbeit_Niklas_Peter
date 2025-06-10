from src.rebuilding_command_line_service import RebuildingCommandLineService


def debug_run():
    control_time = input("Zu welcher Zeit (in Sekunden) soll der Stand der Simulation ausgegeben werden?: ")
    buck_fixing_command_line_service = RebuildingCommandLineService(control_time)
    buck_fixing_command_line_service.start_simulation()

if __name__ == '__main__':
    debug_run()
