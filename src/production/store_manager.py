from simpy import Store

from src.order_data.product import Product
from src.order_data.production_material import ProductionMaterial


class StoreManager:

    def __init__(self, simulation_environment):
        self.env = simulation_environment

    def count_products_in_store(self, store: Store, product_type: Product | ProductionMaterial) -> int:
        return sum(1 for item in store.items if item == product_type)

    def count_empty_space_in_store(self, store: Store) -> int:
        store_capacity = store.capacity
        quantity_of_stored_item = len(store.items)
        return (store_capacity - quantity_of_stored_item)

