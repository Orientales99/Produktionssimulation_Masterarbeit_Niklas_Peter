from src.entity.working_robot.working_robot import WorkingRobot


class ConvertWrToDict:
    def __init__(self):
        pass

    def serialize_complete_working_robot(self, wr: WorkingRobot) -> dict:
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
                "side step driving route": wr.working_status.side_step_driving_route if
                wr.working_status.side_step_driving_route else None
            }
        }

    def serialize_shorted_version_working_robot(self, wr: WorkingRobot) -> dict:
        return {
            "identification_str": wr.identification_str,
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
                "side step driving route": wr.working_status.side_step_driving_route if
                wr.working_status.side_step_driving_route else None
            }
        }

    def safe_coords_list(self, coord_list):
        """Secure access to coordinate lists with error handling."""
        if coord_list is not None:
            if isinstance(coord_list, list):
                return coord_list if coord_list else None
            else:
                return None