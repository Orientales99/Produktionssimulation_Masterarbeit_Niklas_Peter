from simpy import Store
from collections import Counter, defaultdict
from src.order_data.product import Product
from src.order_data.production_material import ProductionMaterial


class StoreManager:

    def __init__(self, simulation_environment):
        self.env = simulation_environment

    def count_number_of_one_product_type_in_store(self, store: Store,
                                                  product_type: Product | ProductionMaterial) -> int:
        return sum(1 for item in store.items if item == product_type)

    def count_empty_space_in_store(self, store: Store) -> int:
        store_capacity = store.capacity
        quantity_of_stored_item = len(store.items)
        return (store_capacity - quantity_of_stored_item)

    def get_material_out_of_store(self, store: Store, material: ProductionMaterial) -> Store:
        list_store_items: list[ProductionMaterial]
        list_store_items = store.items
        material_identification_str = material.identification_str
        for item in list_store_items:
            if item.identification_str == material_identification_str:
                list_store_items.remove(item)
                break
        store.items = list_store_items
        return store

    def get_most_common_product_in_store(self, store: Store) -> ProductionMaterial | None:
        if not store.items:
            return None  # return None if store is empty

        id_list = [item.identification_str for item in store.items]

        # count how often each identification_str occurs
        counter = Counter(id_list)

        most_common_id, _ = counter.most_common(1)[0]

        for item in store.items:
            if item.identification_str == most_common_id:
                return item

        return None

    def check_no_other_material_is_in_store(self, store: Store, material: ProductionMaterial) -> bool:
        """ Check if all items in the store have the same identification_str.
            Return True: all items have same identification_str or no item is in Store
            Return False: Other item than material are in store
            """

        items = list(store.items)

        if not items:
            return True  # Leerer Store → keine widersprüchlichen Materialien

        for item in items:
            if item.identification_str != material.identification_str:
                return False
        return True

    def get_str_products_in_store(self, store: Store) -> str:
        """Finds all different ProductionMaterial.identification_str and counts their frequency."""
        item_counts = defaultdict(int)
        item_count_str = ""

        for item in store.items:
            identification_str = item.identification_str
            item_counts[identification_str] += 1

        for identification, count in item_counts.items():
            item_count_str_part = str(f"Produkt-ID '{identification}' kommt {count} mal vor.\n")
            item_count_str += item_count_str_part

        if item_count_str == "":
            item_count_str = "0"

        return item_count_str


    def get_dict_number_of_products_in_store(self, store: Store) -> dict[str, int]:
        """Finds all different ProductionMaterial.identification_str and counts their frequency. Put them in dict"""
        item_counts = defaultdict(int)

        for item in store.items:
            identification_str = item.identification_str
            item_counts[identification_str] += 1

        return dict(item_counts)