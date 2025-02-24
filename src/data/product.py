from src.data.constant import ItemType


class Product:
    name: str
    size: int               # Europalette = 100 units
    item_type: ItemType

    def __init__(self, name, size, item_type):
        self.name = name
        self.size = size
        self.item_type = item_type
