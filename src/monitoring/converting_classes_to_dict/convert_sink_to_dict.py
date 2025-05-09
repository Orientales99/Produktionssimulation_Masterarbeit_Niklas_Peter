from src.constant.constant import ItemType, ProductGroup
from src.entity.sink import Sink
from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial
from src.production.base.coordinates import Coordinates
from src.production.store_manager import StoreManager


class ConvertSinkTDict:
    def __init__(self, store_manager: StoreManager):
        self.store_manager = store_manager

    def serialize_complete_sink(self, sink: Sink) -> dict:
        products_in_goods_issue_store = self.store_manager.get_dict_number_of_products_in_store(sink.goods_issue_store)
        goods_issue_order_list = self.goods_issue_order_list(sink.goods_issue_order_list)
        if sink.goods_issue_store.capacity == float("inf"):
            max_capacity = "Infinity"
        else:
            max_capacity = sink.goods_issue_store.capacity

        return {
            "goods_issue_store": {
                "Max Capacity": max_capacity,
                "Contained Units": len(sink.goods_issue_store.items),
                "Loaded Products": products_in_goods_issue_store
            },
            "goods_issue_order_list": goods_issue_order_list
        }

    def goods_issue_order_list(self,  goods_issue_order_list: list[(Order, int)]) -> list[dict]:
        goods_issue_order_dict_list = []
        for order, number_of_produced_items in goods_issue_order_list:
            order_dict = {
                "product_identification": order.product.identification_str,
                "order_date": str(order.order_date),
                "number_of_products": order.number_of_products_per_order,
                "priority": order.priority.name,
                "daily_manufacturing_sequence": order.daily_manufacturing_sequence,
                "number_of_produced_items": number_of_produced_items
            }
            goods_issue_order_dict_list.append(order_dict)

        return goods_issue_order_dict_list

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