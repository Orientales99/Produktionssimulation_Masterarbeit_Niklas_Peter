import simpy
from simpy import Store

from src.constant.constant import ItemType, ProductGroup
from src.entity.intermediate_store import IntermediateStore
from src.order_data.production_material import ProductionMaterial
from src.production.base.coordinates import Coordinates


class ConvertDictToIntermediateStore:
    def __init__(self, env: simpy.Environment):
        self.env = env

    def deserialize_complete_intermediate_store(self, intermediate_store_dict: dict) -> IntermediateStore:
        entity_data = intermediate_store_dict["entities"][0]["entity_data"]
        size = Coordinates(entity_data["size"]["x"], entity_data["size"]["y"])
        store = self.rebuild_intermediate_store(entity_data["intermediate_store"])

        return IntermediateStore(
            identification_number=entity_data["identification_number"],
            driving_speed=entity_data["driving_speed"],
            size=size,
            intermediate_store=store
        )

    def rebuild_intermediate_store(self, storage_dict: dict) -> Store:
        contained_units = storage_dict["Contained Units"]
        if contained_units != 0:
            storage = storage_dict["Loaded Products"]

            store_capacity = storage_dict["Max Capacity"]
            if storage_dict["Max Capacity"] == "Infinity":
                store_capacity = float("inf")

            store = Store(self.env, capacity=store_capacity)

            for identification_str in storage:
                production_material = self.rebuild_production_material_from_ident_str(identification_str)
                quantity = storage_dict["Loaded Products"][identification_str]
                for _ in range(quantity):
                    store.items.append(production_material)
        else:
            store = Store(self.env)
        return store

    def rebuild_production_material_from_ident_str(self, ident_str: str) -> ProductionMaterial | None:
        """
        Rebuilds a ProductionMaterial object from its identification string.
        Extracts information like ProductGroup, ItemType, and Size.
        """
        # Example of how to split the identification string
        if ident_str is None:
            return None
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
