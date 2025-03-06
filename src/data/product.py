from src.data.constant import ItemType


class Product:
    product_id: int
    size: int               # Europalette = 100 units
    item_type: ItemType

    def __init__(self, product_id, size, item_type):
        self.product_id = product_id
        self.size = size
        self.item_type = item_type
