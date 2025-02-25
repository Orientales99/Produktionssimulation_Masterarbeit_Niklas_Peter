from src.data.constant import MachineQuality
from src.data.product import Product


class Machine:
    type_number: int
    machine_quality: MachineQuality
    driving_speed: int
    working_speed: int
    machine_size: tuple
    max_loading_capacity_product_before_process: int
    quantity_loaded_product_before_processed: int
    loaded_product_before_processed: Product
    max_loading_capacity_product_after_process: int
    quantity_loaded_product_after_processed: int
    loaded_product_after_processed: Product
    working_robot_on_machine: bool
    producing_product: Product
    setting_up_time: int

    def __init__(self, type_number, machine_quality, driving_speed, working_speed, machine_size,
                 max_loading_capacity_product_before_process, quantity_loaded_product_before_processed,
                 loaded_product_before_processed, max_loading_capacity_product_after_process,
                 quantity_loaded_product_after_processed,
                 loaded_product_after_processed, working_robot_on_machine, producing_product, setting_up_time):
        self.type_number = type_number
        self.machine_quality = machine_quality
        self.driving_speed = driving_speed
        self.working_speed = working_speed
        self.machine_size = machine_size
        self.max_loading_capacity_product_before_process = max_loading_capacity_product_before_process
        self.quantity_loaded_product_before_processed = quantity_loaded_product_before_processed
        self.loaded_product_before_processed = loaded_product_before_processed
        self.max_loading_capacity_product_after_process = max_loading_capacity_product_after_process
        self.quantity_loaded_product_after_processed = quantity_loaded_product_after_processed
        self.loaded_product_after_processed = loaded_product_after_processed
        self.working_robot_on_machine = working_robot_on_machine
        self.producing_product = producing_product
        self.setting_up_time = setting_up_time
