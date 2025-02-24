class TransportRobot:
    type_number: int
    driving_speed: int
    loading_capacity: int

    def __init__(self, type_number, driving_speed, loading_capacity):
        self.type_number = type_number
        self.driving_speed = driving_speed
        self.loading_capacity = loading_capacity

