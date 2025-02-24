from src.data.constant import MachineQuality
from src.data.product import Product


class Machine:
    type_number: int
    machine_quality: MachineQuality
    driving_speed: int
    working_speed: int
    loading_capacity_product_before_process: int
    loading_capacity_product_after_process: int
    working_robot_on_machine: bool
    producing_product: Product
    setting_up_time: int

    def __init__(self, type_number, machine_quality, driving_speed, working_speed,
                 loading_capacity_product_before_process, loading_capacity_product_after_process,
                 working_robot_on_machine, producing_product, setting_up_time):

        self.type_number = type_number
        self.machine_quality = machine_quality
        self.driving_speed = driving_speed
        self.working_speed = working_speed
        self.loading_capacity_product_before_process = loading_capacity_product_before_process
        self.loading_capacity_product_after_process = loading_capacity_product_after_process
        self.working_robot_on_machine = working_robot_on_machine
        self.producing_product = producing_product
        self.setting_up_time = setting_up_time


