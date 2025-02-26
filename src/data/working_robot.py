class WorkingRobot:
    identification_number: int
    robot_size: tuple
    driving_speed: int
    product_transfer_rate: int


    def __init__(self, identification_number, robot_size, driving_speed, product_transfer_rate):
        self.identification_number = identification_number
        self.robot_size = robot_size
        self.driving_speed = driving_speed
        self.product_transfer_rate = product_transfer_rate
