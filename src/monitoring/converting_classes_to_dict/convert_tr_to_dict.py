from src.entity.transport_robot.transport_robot import TransportRobot
from src.production.store_manager import StoreManager


class ConvertTrToDict:
    store_manager: StoreManager

    def __init__(self, store_manager):
        self.store_manager = store_manager

    def serialize_complete_transport_robot(self, tr: TransportRobot) -> dict:
        products_in_tr_store = self.store_manager.get_dict_number_of_products_in_store(tr.material_store)
        return {
            "identification_str": tr.identification_str,
            "size": {
                "x": tr.size.x,
                "y": tr.size.y
            },
            "loading_speed": tr.loading_speed,
            "driving_speed": tr.driving_speed,
            "material_store": {
                "Max Capacity": tr.material_store.capacity,
                "Contained Units": len(tr.material_store.items),
                "Loaded Products": products_in_tr_store
            },
            "working_status": {
                "status": tr.working_status.status.name,
                "working on status": tr.working_status.working_on_status,
                "waiting time on path": tr.working_status.waiting_time_on_path,
                "driving destination coordinates": ({"x": tr.working_status.driving_destination_coordinates.x,
                                                     "y": tr.working_status.driving_destination_coordinates.y}
                                                    if tr.working_status.driving_destination_coordinates else None),
                "driving route": self.safe_coords_list(tr.working_status.driving_route),
                "destination location entity": tr.working_status.destination_location_entity.identification_str if
                tr.working_status.destination_location_entity else None,
                "side_step_driving_route": tr.working_status.side_step_driving_route if
                tr.working_status.side_step_driving_route else None,
                "waiting_time_error": tr.working_status.waiting_error_time
            },
            "transport_order": (
                {
                    "unload destination": tr.transport_order.unload_destination.identification_str
                    if tr.transport_order.unload_destination else None,
                    "pick up station": tr.transport_order.pick_up_station.identification_str
                    if tr.transport_order.pick_up_station else None,
                    "transporting product": tr.transport_order.transporting_product.identification_str
                    if tr.transport_order.transporting_product else None,
                    "quantity": tr.transport_order.quantity
                } if tr.transport_order else None
            )
        }

    def safe_coords_list(self, coord_list):
        """Secure access to coordinate lists with error handling."""
        if coord_list is not None:
            if isinstance(coord_list, list):
                return coord_list if coord_list else None
            else:
                return None
