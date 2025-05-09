from src.entity.working_robot.working_robot import WorkingRobot
from src.production.base.cell import Cell


class ConvertWrToDict:
    def __init__(self):
        pass

    def serialize_complete_working_robot(self, wr: WorkingRobot) -> dict:

        if wr.working_status.last_placement_in_production is not None:
            last_placement_in_production = self.get_list_cell_as_str(wr.working_status.last_placement_in_production)
            print(wr.working_status.last_placement_in_production)
        else:
            last_placement_in_production = None

        return {
            "identification_str": wr.identification_str,
            "size": {
                "x": wr.size.x,
                "y": wr.size.y
            },
            "driving_speed": wr.driving_speed,
            "product_transfer_rate": wr.product_transfer_rate,
            "working_status": {
                "status": wr.working_status.status.name,
                "working on status": wr.working_status.working_on_status,
                "in production": wr.working_status.in_production,
                "waiting time on path": wr.working_status.waiting_time_on_path,
                "working for machine": wr.working_status.working_for_machine.identification_str if
                wr.working_status.working_for_machine else None,
                "driving destination coordinates": (
                    {"x": wr.working_status.driving_destination_coordinates.x,
                     "y": wr.working_status.driving_destination_coordinates.y}
                    if wr.working_status.driving_destination_coordinates
                    else None
                ),
                "driving route": self.safe_coords_list(wr.working_status.driving_route),
                "side step driving route": wr.working_status.side_step_driving_route,
                "last placement in production": last_placement_in_production
            }
        }

    def safe_coords_list(self, coord_list) -> list[str]:
        """Secure access to coordinate lists with error handling."""
        coordinate_list = []
        if not isinstance(coord_list, list):
            return coordinate_list

        if len(coord_list) != 0:
            for coordinate in coord_list:
                coordinate_list.append(coordinate)
        return coordinate_list

    def get_list_cell_as_str(self, cell_list: list[Cell]) -> list[str]:
        str_cells = []
        for cell in cell_list:
            str_cells.append(f"({cell.cell_id})")
        return str_cells
