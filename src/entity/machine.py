from dataclasses import dataclass, field

from src.constant.constant import MachineQuality
from src.order_data.order import Order
from src.order_data.product import Product
from src.production.base.coordinates import Coordinates
from src.entity.machine_storage import MachineStorage
from src.order_data.production_material import ProductionMaterial


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

    processing_list: list[(Order, int)] = field(
        default_factory=list)  # default: empty | list (Order, step of the process)
    required_material_list: list[(ProductionMaterial, int)] = field(
        default_factory=list)  # default: empty | list (ProductionMaterial, necessary quantity)
    processing_list_queue_length: float = 0
    waiting_for_arriving_of_wr: bool = False

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
                    self.processing_list_queue_length += (
                                                                 int(number_of_required_products) * time_to_process_one_product) + \
                                                         self.setting_up_time
                elif order.product == self.producing_product:
                    self.processing_list_queue_length += (
                            int(number_of_required_products) * time_to_process_one_product)
                else:
                    return Exception("Queue length cannot be calculated probably")

        if self.machine_quality == MachineQuality.OLD_MACHINE:
            self.processing_list_queue_length += self.processing_list_queue_length * 0.2

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

    def get_list_with_required_material(self) -> list[(ProductionMaterial, int)]:
        """get a list with required material and quantity based on the processing_list"""
        self.required_material_list = []
        for order, step_of_the_process in self.processing_list:
            data_processing_step = self.get_data_of_processing_step_for_machine(order)
            required_material = data_processing_step[0]
            quantity_in_store = sum(1 for item in self.machine_storage.storage_before_process.items
                                    if item.identification_str == required_material.identification_str)
            quantity_of_necessary_material = order.number_of_products_per_order - quantity_in_store

            self.required_material_list.append((required_material, quantity_of_necessary_material))

        return self.required_material_list

    def get_data_of_processing_step_for_machine(self, order: Order) -> tuple[ProductionMaterial, int]:
        """gives a tuple with required product type for this step and the processing_time_per_product"""
        if order.product.processing_step_1 == self.machine_type:
            processing_step = (order.product.required_product_type_step_1, order.product.processing_time_step_1)

        if order.product.processing_step_2 == self.machine_type:
            processing_step = (order.product.required_product_type_step_2, order.product.processing_time_step_2)

        if order.product.processing_step_3 == self.machine_type:
            processing_step = (order.product.required_product_type_step_3, order.product.processing_time_step_3)

        if order.product.processing_step_4 == self.machine_type:
            processing_step = (order.product.required_product_type_step_4, order.product.processing_time_step_4)

        return processing_step
