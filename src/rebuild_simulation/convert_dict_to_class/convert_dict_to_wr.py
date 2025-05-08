from src.entity.working_robot.working_robot import WorkingRobot
from src.entity.working_robot.wr_working_status import WrWorkingStatus
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates


class ConvertDictToWr:
    def __init__(self):
        pass

    def deserialize_complete_working_robot(self, wr_dict: dict) -> WorkingRobot:
        # Extrahieren der Basis-Attribute des Working Robots
        size_data = wr_dict.get("size", {})
        working_status_data = wr_dict.get("working_status", {})

        # Erstellen der Size-Instanz
        size = Coordinates(x=size_data.get("x", 0), y=size_data.get("y", 0))

        if working_status_data.get("last placement in production") is not None:
            last_placement_in_production = self.get_cell_list_for_last_placement(working_status_data.get("last_placement_in_production"))
        else:
            last_placement_in_production = None

        # Erstellen des WrWorkingStatus-Objekts
        working_status = WrWorkingStatus(
            status=working_status_data.get("status", ""),
            working_on_status=working_status_data.get("working on status", ""),
            in_production=working_status_data.get("in production", False),
            waiting_time_on_path=working_status_data.get("waiting time on path", 0),
            working_for_machine=self._get_machine_by_id(working_status_data.get("working for machine")),
            driving_destination_coordinates=self._get_coordinates(
                working_status_data.get("driving destination coordinates")),
            driving_route=self._get_coords_list(working_status_data.get("driving route")),
            side_step_driving_route=working_status_data.get("side step driving route", None),
            last_placement_in_production=last_placement_in_production
        )

        # Extrahieren der Identifikationsnummer (jetzt als int)
        identification_number = wr_dict.get("identification_number", 0)

        # Erstellen des WorkingRobot-Objekts
        wr = WorkingRobot(
            identification_number=identification_number,
            size=size,
            driving_speed=wr_dict.get("driving_speed", 0),
            product_transfer_rate=wr_dict.get("product_transfer_rate", 0),
            working_status=working_status
        )

        return wr

    def _get_machine_by_id(self, machine_id: str):
        """Fetches a machine based on its ID. A placeholder is used here."""
        # Hier kannst du z. B. auf eine Liste oder ein Dictionary von Maschinen zugreifen.
        # Für dieses Beispiel gehe ich davon aus, dass ein Mapping existiert, aber es könnte auch eine DB-Abfrage sein.
        return None  # Platzhalter, da der Zugriff auf Maschinen fehlt

    def _get_coordinates(self, coords_dict: dict):
        """Auxiliary method for extracting coordinates from a dict and converting them to a tuple."""
        if coords_dict and isinstance(coords_dict, dict):
            return Coordinates(x=coords_dict.get("x", 0), y=coords_dict.get("y", 0))
        return None

    def _get_coords_list(self, coords_list):
        """Saves access to lists of coordinates and returns them."""
        if isinstance(coords_list, list):
            return coords_list if coords_list else []
        return []

    def get_cell_list_for_last_placement(self, str_cells: str) -> list[Cell]:
        list_cell: list[Cell] = []

        for cell_str in str_cells:

            clean_str = cell_str.strip("()")
            x_str, y_str = clean_str.split(":")
            x, y = int(x_str), int(y_str)


            cell = Cell(
                cell_coordinates=Coordinates(x=x, y=y),
                placed_entity=None
            )
            list_cell.append(cell)

        return list_cell
