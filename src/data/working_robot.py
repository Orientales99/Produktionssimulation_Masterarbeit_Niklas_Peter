class WorkingRobot:
    type_number: int
    driving_speed: int
    product_transfer_rate: int

    def __init__(self, type_number, driving_speed, product_transfer_rate):
        self.type_number = type_number
        self.driving_speed = driving_speed
        self.product_transfer_rate = product_transfer_rate
