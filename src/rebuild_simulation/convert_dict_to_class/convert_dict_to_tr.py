import simpy

from src.constant.constant import ProductGroup, ItemType

from src.entity.transport_robot.tr_working_status import TrWorkingStatus
from src.entity.transport_robot.transport_order import TransportOrder
from simpy import Store

from src.entity.transport_robot.transport_robot import TransportRobot
from src.order_data.production_material import ProductionMaterial
from src.production.base.coordinates import Coordinates


class ConvertDictToTr:
    def __init__(self, env: simpy.Environment, machine_dict=None, source_dict=None, sink_dict=None):
        self.env = env
        self.machine_dict = machine_dict or {}
        self.source_dict = source_dict or {}
        self.sink_dict = sink_dict or {}

    def deserialize_complete_transport_robot(self, tr_dict: dict) -> TransportRobot:
        size = self._extract_coordinates(tr_dict.get("size", {}))
        material_store = self._rebuild_material_store(tr_dict.get("material_store", {}))
        working_status = self._rebuild_working_status(tr_dict.get("working_status", {}))
        transport_order = self._rebuild_transport_order(tr_dict.get("transport_order", None))

        return TransportRobot(
            identification_number=self._extract_identification_number(tr_dict.get("identification_str", "")),
            size=size,
            loading_speed=tr_dict.get("loading_speed", 0),
            driving_speed=tr_dict.get("driving_speed", 0),
            material_store=material_store,
            working_status=working_status,
            transport_order=transport_order
        )

    def _extract_identification_number(self, identification_str: str) -> int:
        # Extracts the numeric part from the identification string e.g. "TR: 5" -> 5
        return int(identification_str.split(":")[1].strip()) if ":" in identification_str else 0

    def _extract_coordinates(self, coords_dict: dict) -> Coordinates:
        return Coordinates(x=coords_dict.get("x", 0), y=coords_dict.get("y", 0))

    def _rebuild_material_store(self, material_store_dict: dict) -> Store:
        # Create a new Store and fill it with reconstructed ProductionMaterials
        store = Store(self.env, capacity=material_store_dict.get("Max Capacity", 1))
        loaded_products = material_store_dict.get("Loaded Products", {})
        for ident_str, quantity in loaded_products.items():
            product = self._rebuild_production_material_from_ident_str(ident_str)
            for _ in range(quantity):
                store.items.append(product)
        return store

    def _rebuild_production_material_from_ident_str(self, ident_str: str) -> ProductionMaterial | None:
        # Example: "SEVEN.0" -> ProductGroup.SEVEN, ItemType=0
        try:
            group_str, item_type_str = ident_str.split(".")
            group = ProductGroup[group_str]
            item_type = ItemType(int(item_type_str))
            return ProductionMaterial(
                identification_str=ident_str,
                production_material_id=group,
                size=Coordinates(1, 1),  # Default or reconstruct separately if needed
                item_type=item_type
            )
        except Exception as e:
            print(f"Error rebuilding product: {ident_str}, {e}")
            return None

    def _rebuild_working_status(self, status_dict: dict) -> TrWorkingStatus:
        return TrWorkingStatus(
            status=status_dict.get("status", ""),
            working_on_status=status_dict.get("working on status", ""),
            waiting_time_on_path=status_dict.get("waiting time on path", 0),
            driving_destination_coordinates=self._extract_coordinates(
                status_dict.get("driving destination coordinates", {})
            ),
            driving_route=self._rebuild_coords_list(status_dict.get("driving route")),
            destination_location_entity=self._get_entity_by_id(status_dict.get("destination location entity")),
            side_step_driving_route=status_dict.get("side step driving route"),
            waiting_error_time=status_dict.get("waiting_time_error")
        )

    def _rebuild_coords_list(self, coords_list) -> list[Coordinates]:
        if isinstance(coords_list, list):
            return [self._extract_coordinates(c) for c in coords_list]
        return []

    def _rebuild_transport_order(self, order_dict: dict | None) -> TransportOrder | None:
        if not order_dict:
            return None
        return TransportOrder(
            unload_destination=self._get_entity_by_id(order_dict.get("unload destination")),
            pick_up_station=self._get_entity_by_id(order_dict.get("pick up station")),
            transporting_product=self._rebuild_production_material_from_ident_str(
                order_dict.get("transporting product")
            ),
            quantity=order_dict.get("quantity", 0)
        )

    def _get_entity_by_id(self, entity_id: str):
        # Tries to find the referenced entity by ID from the provided entity dictionaries
        if not entity_id:
            return None
        return (
                self.machine_dict.get(entity_id) or
                self.source_dict.get(entity_id) or
                self.sink_dict.get(entity_id)
        )
