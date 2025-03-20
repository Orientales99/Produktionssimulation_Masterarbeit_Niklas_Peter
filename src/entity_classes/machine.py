from dataclasses import dataclass, field

from src.data.constant import MachineQuality
from src.data.order import Order
from src.data.product import Product
from src.data.coordinates import Coordinates
from src.data.machine_storage import MachineStorage


@dataclass
class Machine:
    machine_type: int
    identification_number: int
    machine_quality: MachineQuality
    driving_speed: int
    working_speed: int
    size: Coordinates
    machine_storage: MachineStorage
    working_robot_on_machine: bool
    producing_product: Product | None
    setting_up_time: float  # Rüstzeit
    processing_list: list[Order, int] = field(
        default_factory=list)  # default: empty | list (Order, step of the process)
    processing_list_queue_length: float = 0

    @property  # only if identification_str is used; one time calculation -> is cached
    def identification_str(self) -> str:
        return f"Ma: {self.machine_type}, {self.identification_number}"

    def calculating_processing_list_queue_length(self):
        if len(self.processing_list) != 0:
            self.processing_list_queue_length = float(0)
            for order, step_of_the_process in self.processing_list:
                number_of_required_products = order.number_of_products_per_order
                time_to_process_one_product = self.get_time_to_process_one_product(order, step_of_the_process)
                if order.product != self.producing_product:
                    self.processing_list_queue_length += (int(number_of_required_products) * time_to_process_one_product) +\
                                                         self.setting_up_time
                elif order.product == self.producing_product:
                    self.processing_list_queue_length += (int(number_of_required_products) * time_to_process_one_product)
                else:
                    return Exception("Queue length cannot be calculated probably")
        return self.processing_list_queue_length

    def get_time_to_process_one_product(self, order, step_of_the_process) -> float:
        if step_of_the_process == 1:
            time_to_process_one_product = order.product.processing_time_step_1

        if step_of_the_process == 2:
            time_to_process_one_product = order.product.processing_time_step_2

        if step_of_the_process == 3:
            time_to_process_one_product = order.product.processing_time_step_3

        if step_of_the_process == 4:
            time_to_process_one_product = order.product.processing_time_step_4

        return time_to_process_one_product