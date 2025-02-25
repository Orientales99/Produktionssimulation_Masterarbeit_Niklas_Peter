from src.data.product import Product
class TransportRobot:
    type_number: int
    driving_speed: int
    loaded_capacity: int
    max_loading_capacity: int
    product: Product

    def __init__(self, type_number, product, driving_speed, loaded_capacity, max_loading_capacity):
        self.type_number = type_number
        self.product = product
        self.driving_speed = driving_speed
        self.loading_capacity = loaded_capacity
        self.max_loading_capacity = max_loading_capacity


