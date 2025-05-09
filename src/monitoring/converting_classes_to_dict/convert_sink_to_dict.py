from src.entity.sink import Sink
from src.order_data.order import Order
from src.production.store_manager import StoreManager


class ConvertSinkTDict:
    def __init__(self, store_manager: StoreManager):
        self.store_manager = store_manager

    def serialize_complete_sink(self, sink: Sink) -> dict:
        products_in_goods_issue_store = self.store_manager.get_dict_number_of_products_in_store(sink.goods_issue_store)
        goods_issue_order_list = self.goods_issue_order_list(sink.goods_issue_order_list)

        return {
            "goods_issue_store": {
                "Max Capacity": sink.goods_issue_store.capacity,
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