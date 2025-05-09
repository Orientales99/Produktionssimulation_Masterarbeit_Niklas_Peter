from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot
from src.monitoring.converting_classes_to_dict.convert_machine_to_dict import ConvertMachineToDict
from src.monitoring.converting_classes_to_dict.convert_sink_to_dict import ConvertSinkTDict
from src.monitoring.converting_classes_to_dict.convert_tr_to_dict import ConvertTrToDict
from src.monitoring.converting_classes_to_dict.convert_wr_to_dict import ConvertWrToDict

from src.production.base.cell import Cell
from src.production.store_manager import StoreManager


class ConvertCellToDict:
    convert_machine_to_dict: ConvertMachineToDict
    convert_wr_to_dict: ConvertWrToDict
    convert_tr_to_dict: ConvertTrToDict
    store_manager: StoreManager

    def __init__(self, store_manager):
        self.store_manager = store_manager
        self.convert_machine_to_dict = ConvertMachineToDict(self.store_manager)
        self.convert_wr_to_dict = ConvertWrToDict()
        self.convert_tr_to_dict = ConvertTrToDict(self.store_manager)
        self.convert_sink_to_dict = ConvertSinkTDict(self.store_manager)

    def start_converting_cell_during_simulation(self, cell: Cell) -> dict:
        base_dict = {
            "x": cell.cell_coordinates.x,
            "y": cell.cell_coordinates.y,
            "entity_type": None,
            "entity_id": None,
            "entity_data": None
        }

        entity = cell.placed_entity
        if entity is None:
            return base_dict

        base_dict["entity_type"] = entity.__class__.__name__

        if isinstance(entity, Machine):
            base_dict["entity_data"] = self.convert_machine_to_dict.serialize_complete_machine(entity)

        if isinstance(entity, WorkingRobot):
            base_dict["entity_data"] = self.convert_wr_to_dict.serialize_complete_working_robot(entity)

        if isinstance(entity, TransportRobot):
            base_dict["entity_data"] = self.convert_tr_to_dict.serialize_complete_transport_robot(entity)

        if isinstance(entity, Sink):
            base_dict["entity_data"] = self.convert_sink_to_dict.serialize_complete_sink(entity)

        return base_dict

