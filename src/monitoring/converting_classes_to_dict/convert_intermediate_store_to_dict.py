from src.entity.intermediate_store import IntermediateStore
from src.production.store_manager import StoreManager


class ConvertIntermediateStoreToDict:
    def __init__(self, store_manager: StoreManager):
        self.store_manager = store_manager

    def serialize_complete_machine(self, intermediate_store: IntermediateStore):
        products_in_store = self.store_manager.get_dict_number_of_products_in_store(intermediate_store.intermediate_store)
        if intermediate_store.intermediate_store.capacity == float("inf"):
            max_capacity = "Infinity"
        else:
            max_capacity = intermediate_store.intermediate_store.capacity
        return{
            "identification_number": intermediate_store.identification_number,
            "identification_str": intermediate_store.identification_str,
            "driving_speed": intermediate_store.driving_speed,
            "size": {
                "x": intermediate_store.size.x,
                "y": intermediate_store.size.y
            },
            "intermediate_store":{
                "Max Capacity": max_capacity,
                "Contained Units": len(intermediate_store.intermediate_store.items),
                "Loaded Products": products_in_store
            }
        }
