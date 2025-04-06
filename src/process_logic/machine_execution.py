from datetime import date

from src.constant.constant import MachineQuality
from src.entity.machine import Machine
from src.entity.required_material import RequiredMaterial
from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial

class MachineExecution:
    machine_list: list[Machine]
    list_full_store_after_process = list[Machine]


    def __init__(self, production):
        self.production = production
        self.machine_list = self.production.machine_list

        self.list_full_store_after_process = []
        self.material_transport_request_list = []

    def create_tr_process_order_list(self):

        pass

    def check_any_machine_store_after_process_full(self):
        for machine in self.machine_list:
            if len(machine.machine_storage.storage_after_process.items) >= machine.machine_storage.storage_after_process.capacity:
                self.list_full_store_after_process.append(machine)

    def check_for_starting_machine_process(self):
        """Checking if the machine can start the production of production"""
        for machine in self.machine_list:
            if machine not in self.list_full_store_after_process:
                if machine.processing_list > 0:
                    if machine.working_robot_on_machine is True or machine.waiting_for_arriving_of_wr is True:
                        order, step = machine.processing_list[0]
                        required_material = f'required_product_type_step_{step}'
                        if required_material in machine.machine_storage.storage_before_process.items:
                            self.start_process(machine)


                        else:  # request_tr
                            pass
                    else:  # request wr
                        pass
            else:  # check for new orders
                pass

    def start_process_of_machine(self, machine):
        pass

    def calculating_processing_list_queue_length(self, machine: Machine):
        if len(machine.processing_list) != 0:
            machine.processing_list_queue_length = float(0)
            for order, step_of_the_process in machine.processing_list:
                number_of_required_products = order.number_of_products_per_order
                time_to_process_one_product = self.get_time_to_process_one_product(order, step_of_the_process)
                if order.product != machine.producing_product:
                    machine.processing_list_queue_length += (
                                                                 int(number_of_required_products) * time_to_process_one_product) + \
                                                         machine.setting_up_time
                elif order.product == machine.producing_product:
                    machine.processing_list_queue_length += (
                            int(number_of_required_products) * time_to_process_one_product)
                else:
                    return Exception("Queue length cannot be calculated probably")

        if machine.machine_quality == MachineQuality.OLD_MACHINE:
            machine.processing_list_queue_length += machine.processing_list_queue_length * 0.2

        return machine.processing_list_queue_length

    def get_time_to_process_one_product(self, order, step_of_the_process) -> float:
        if step_of_the_process == 1:
            time_to_process_one_product = order.product.processing_time_step_1
            return time_to_process_one_product

        if step_of_the_process == 2:
            time_to_process_one_product = order.product.processing_time_step_2
            return time_to_process_one_product

        if step_of_the_process == 3:
            time_to_process_one_product = order.product.processing_time_step_3
            return time_to_process_one_product

        if step_of_the_process == 4:
            time_to_process_one_product = order.product.processing_time_step_4
            return time_to_process_one_product


    def get_list_with_required_material(self, machine: Machine) -> list[RequiredMaterial]:
        """get a list with required material and quantity based on the processing_list"""
        machine.required_material_list = []
        for order, step_of_the_process in machine.processing_list:
            data_processing_step = self.get_data_of_processing_step_for_machine(order, machine)
            required_material = data_processing_step[0]
            quantity_in_store = sum(1 for item in machine.machine_storage.storage_before_process.items
                                    if item.identification_str == required_material.identification_str)
            quantity_of_necessary_material = order.number_of_products_per_order - quantity_in_store

            machine.required_material_list.append(RequiredMaterial(required_material, quantity_of_necessary_material))

        return machine.required_material_list

    def get_data_of_processing_step_for_machine(self, order: Order, machine: Machine) -> tuple[ProductionMaterial, int]:
        """gives a tuple with required product type for this step and the processing_time_per_product"""
        if order.product.processing_step_1 == machine.machine_type:
            processing_step = (order.product.required_product_type_step_1, order.product.processing_time_step_1)

        if order.product.processing_step_2 == machine.machine_type:
            processing_step = (order.product.required_product_type_step_2, order.product.processing_time_step_2)

        if order.product.processing_step_3 == machine.machine_type:
            processing_step = (order.product.required_product_type_step_3, order.product.processing_time_step_3)

        if order.product.processing_step_4 == machine.machine_type:
            processing_step = (order.product.required_product_type_step_4, order.product.processing_time_step_4)

        return processing_step