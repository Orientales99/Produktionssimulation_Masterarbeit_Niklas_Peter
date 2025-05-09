from src.constant.constant import WorkingRobotStatus
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.working_robot.working_robot import WorkingRobot
from src.entity.working_robot.wr_working_status import WrWorkingStatus
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.production.production import Production


class ConvertDictToWr:
    every_entity: dict[str, list[Cell]]

    def __init__(self, production: Production):
        self.production = production
        self.every_entity = self.production.entities_init_located

    def deserialize_complete_working_robot(self, wr_dict: dict) -> WorkingRobot:
        # Extrahieren der Basis-Attribute des Working Robots
        entity = wr_dict["entities"][0]["entity_data"]
        size = Coordinates(entity["size"]["x"], entity["size"]["y"])
        working_status_data = wr_dict.get("working_status", {})

        working_status = self.get_working_status(entity["working_status"])

        # Extrahieren der Identifikationsnummer (jetzt als int)
        identification_number = wr_dict.get("identification_number", 0)

        # Erstellen des WorkingRobot-Objekts
        wr = WorkingRobot(
            identification_number=identification_number,
            size=size,
            driving_speed=entity["driving_speed"],
            product_transfer_rate=entity["product_transfer_rate"],
            working_status=working_status
        )

        return wr

    def get_working_status(self, working_status_data: dict) -> WrWorkingStatus:
        # Erstellen des WrWorkingStatus-Objekts
        status = WorkingRobotStatus[working_status_data["status"]]
        working_for_machine = self._get_entity_by_id(working_status_data["working for machine"])
        driving_destination_coordinates = Coordinates(working_status_data["driving destination coordinates"]["x"],
                                                      working_status_data["driving destination coordinates"]["y"])
        last_placement_in_production = self.get_cell_list_for_last_placement(
                                        working_status_data["last placement in production"])

        return WrWorkingStatus(
            status=status,
            working_on_status=working_status_data["working on status"],
            in_production=working_status_data["in production"],
            waiting_time_on_path=working_status_data["waiting time on path"],
            working_for_machine=working_for_machine,
            driving_destination_coordinates=driving_destination_coordinates,
            driving_route=working_status_data["driving route"],
            side_step_driving_route=working_status_data.get("side step driving route", None),
            last_placement_in_production=last_placement_in_production
        )

    def _get_entity_by_id(self, entity_id: str) -> Sink | Source | Machine | None:
        # Tries to find the referenced entity by ID from the provided entity dictionaries

        if entity_id == "Source":
            for y in self.production.production_layout:
                for cell in y:
                    if isinstance(cell.placed_entity, Source):
                        return cell.placed_entity

        elif entity_id == "Sink":
            for y in self.production.production_layout:
                for cell in y:
                    if isinstance(cell.placed_entity, Sink):
                        return cell.placed_entity

        elif entity_id is None:
            return None
        else:
            print(entity_id)
            cell_list = self.every_entity[entity_id]
            print(len(cell_list))
            return cell_list[0].placed_entity

    def get_cell_list_for_last_placement(self, str_cells: str | None) -> list[Cell] | None:
        list_cell: list[Cell] = []
        if str_cells is not None:
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
        return None
