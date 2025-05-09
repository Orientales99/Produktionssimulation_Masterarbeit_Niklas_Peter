import simpy

from src.constant.constant import ProductGroup, ItemType, TransportRobotStatus
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source

from src.entity.transport_robot.tr_working_status import TrWorkingStatus
from src.entity.transport_robot.transport_order import TransportOrder
from simpy import Store

from src.entity.transport_robot.transport_robot import TransportRobot
from src.order_data.production_material import ProductionMaterial
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.production.production import Production


class ConvertDictToTr:
    every_entity: dict[str, list[Cell]]

    def __init__(self, env: simpy.Environment, production: Production):
        self.env = env
        self.production = production
        self.every_entity = self.production.entities_init_located

    def deserialize_complete_transport_robot(self, tr_dict: dict) -> TransportRobot:
        entity = tr_dict["entities"][0]["entity_data"]
        size = Coordinates((entity["size"]["x"]), (entity["size"]["y"]))
        material_store = self._rebuild_material_store(entity["material_store"])
        working_status = self._rebuild_working_status(entity["working_status"])
        transport_order = self._rebuild_transport_order(entity["transport_order"])

        return TransportRobot(
            identification_number=self._extract_identification_number(tr_dict.get("identification_str", "")),
            size=size,
            loading_speed=entity["loading_speed"],
            driving_speed=entity["driving_speed"],
            material_store=material_store,
            working_status=working_status,
            transport_order=transport_order
        )

    def _extract_identification_number(self, identification_str: str) -> int:
        # Extracts the numeric part from the identification string e.g. "TR: 5" -> 5
        return int(identification_str.split(":")[1].strip()) if ":" in identification_str else 0

    def _rebuild_material_store(self, material_store_dict: dict) -> Store:
        # Create a new Store and fill it with reconstructed ProductionMaterials
        contained_units = material_store_dict["Contained Units"]
        max_store_capacity = material_store_dict["Max Capacity"]
        if contained_units != 0:
            for identification_str in material_store_dict["Loaded Products"]:
                production_material = self._rebuild_production_material_from_ident_str(identification_str)
                store = Store(self.env, capacity=max_store_capacity)
                for _ in range(contained_units):
                    store.items.append(production_material)
        else:
            store = Store(self.env, capacity=max_store_capacity)
        return store

    def _rebuild_production_material_from_ident_str(self, ident_str: str) -> ProductionMaterial | None:
        """
        Rebuilds a ProductionMaterial object from its identification string.
        Extracts information like ProductGroup, ItemType, and Size.
        """
        # Example of how to split the identification string
        parts = ident_str.split(".")

        product_group = ProductGroup[parts[1]]  # z.B. 'FIFTEEN' → ProductGroup.FIFTEEN
        item_type = int(parts[2])

        try:
            # Convert the ProductGroup to the enum
            production_material_id = product_group
        except KeyError:
            raise ValueError(f"Invalid ProductGroup in identification string: {product_group}")

        try:
            # Convert the ItemType to the enum
            item_type = ItemType(item_type)
        except ValueError:
            raise ValueError(f"Invalid ItemType in identification string: {item_type}")

        # Assuming a fixed size (or it could be part of the identification string if needed)
        size = Coordinates(x=1, y=1)  # Example size; adjust if necessary

        return ProductionMaterial(
            identification_str=ident_str,
            production_material_id=production_material_id,
            size=size,
            item_type=item_type
        )

    def _rebuild_working_status(self, status_dict: dict) -> TrWorkingStatus:
        status = TransportRobotStatus[status_dict["status"]]
        entity_destination_location_entity = self._get_entity_by_id(status_dict["destination location entity"])
        return TrWorkingStatus(
            status=status,
            working_on_status=status_dict["working on status"],
            waiting_time_on_path=status_dict["waiting time on path"],
            driving_destination_coordinates=Coordinates(status_dict["driving destination coordinates"]["x"],
                                                        status_dict["driving destination coordinates"]["y"]),
            driving_route=status_dict["driving route"],
            destination_location_entity=entity_destination_location_entity,
            side_step_driving_route=status_dict["side_step_driving_route"],
            waiting_error_time=status_dict["waiting_time_error"]
        )

    def _rebuild_transport_order(self, order_dict: dict | None) -> TransportOrder | None:
        if not order_dict:
            return None

        unload_destination = self._get_entity_by_id(order_dict["unload destination"])
        pick_up_station = self._get_entity_by_id(order_dict["pick up station"])
        transporting_product = self._rebuild_production_material_from_ident_str(order_dict["transporting product"])
        return TransportOrder(
            unload_destination=unload_destination,
            pick_up_station=pick_up_station,
            transporting_product=transporting_product,
            quantity=order_dict["quantity"]
        )

    def _get_entity_by_id(self, entity_id: str) -> Sink | Source | Machine:
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

        else:
            cell_list = self.every_entity[entity_id]
            return cell_list[0].placed_entity
