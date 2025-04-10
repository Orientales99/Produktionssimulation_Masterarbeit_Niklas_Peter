from datetime import date

from src.constant.constant import MachineQuality, ItemType
from src.entity.machine import Machine
from src.entity.Process_material import ProcessMaterial
from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial


class Machine_Manager:
    machine_list: list[Machine]
    list_full_store_after_process = list[Machine]

    def __init__(self, production):
        self.production = production
        self.machine_list = self.production.machine_list

        self.list_full_store_after_process = []
        self.material_transport_request_list = []

    def calculating_processing_list_queue_length(self, machine: Machine):
        if len(machine.processing_list) != 0:
            machine.processing_list_queue_length = float(0)
            for processing_order in machine.processing_list:
                number_of_required_products = processing_order.order.number_of_products_per_order
                time_to_process_one_product = self.get_time_to_process_one_product(processing_order.order,
                                                                                   processing_order.step_of_the_process)
                if processing_order.order.product != machine.producing_production_material:
                    machine.processing_list_queue_length += (
                                                                    int(number_of_required_products) * time_to_process_one_product) + \
                                                            machine.setting_up_time
                elif processing_order.order.product == machine.producing_production_material:
                    machine.processing_list_queue_length += (
                            int(number_of_required_products) * time_to_process_one_product)
                else:
                    return Exception("Queue length cannot be calculated probably")

        if machine.machine_quality == MachineQuality.OLD_MACHINE:
            machine.processing_list_queue_length += machine.processing_list_queue_length * 0.2

        return machine.processing_list_queue_length

    def get_time_to_process_one_product(self, order: Order, step_of_the_process: int) -> float:
        if step_of_the_process == 1:
            time_to_process_one_product = order.product.processing_time_step_1
            return time_to_process_one_product

        if step_of_the_process == 2:
            time_to_process_one_product = order.product.processing_time_step_2
            if time_to_process_one_product is None:
                step_of_the_process += 1
            else:
                return time_to_process_one_product

        if step_of_the_process == 3:
            time_to_process_one_product = order.product.processing_time_step_3
            if time_to_process_one_product is None:
                step_of_the_process += 1
            else:
                return time_to_process_one_product

        if step_of_the_process == 4:
            time_to_process_one_product = order.product.processing_time_step_4
            return time_to_process_one_product

    def get_list_with_process_material(self, machine: Machine) -> list[ProcessMaterial]:
        """get a list with required material and quantity based on the processing_list"""
        machine.process_material_list = []
        for processing_order in machine.processing_list:
            # required material
            data_processing_step = self.get_data_of_processing_step_for_machine(processing_order.order, machine)
            required_material = data_processing_step[0]
            quantity_of_necessary_material = processing_order.order.number_of_products_per_order

            # producing material
            producing_material = self.create_new_item_after_process(machine, required_material)
            quantity_of_producing_material = quantity_of_necessary_material

            machine.process_material_list.append(ProcessMaterial(required_material, quantity_of_necessary_material,
                                                                 producing_material, quantity_of_producing_material))

        return machine.process_material_list

    def create_new_item_after_process(self, machine: Machine, item: ProductionMaterial) -> ProductionMaterial:
        """Creating a new ProductionMaterial, identification_str gets an update (ex:# Example: ProductGroup.SEVEN.0 ->
         Example: ProductGroup.SEVEN.1, and item_type (+1).
         Return: new ProductionMaterial"""

        parts = item.identification_str.rsplit(".", 1)
        parts[-1] = str(int(parts[-1]) + 1)
        new_identification_str = ".".join(parts)
        new_item_type = ItemType(item.item_type.value + 1)

        for processing_order in machine.processing_list:
            if processing_order.order.product.product_id == item.production_material_id:
                product = processing_order.order.product

                if (product.required_product_type_step_1 is not None and
                        product.required_product_type_step_1.item_type == new_item_type):
                    return ProductionMaterial(new_identification_str, item.production_material_id, item.size,
                                              new_item_type)

                if (product.required_product_type_step_2 is not None and
                        product.required_product_type_step_2.item_type == new_item_type):
                    return ProductionMaterial(new_identification_str, item.production_material_id, item.size,
                                              new_item_type)

                if (product.required_product_type_step_3 is not None and
                        product.required_product_type_step_3.item_type == new_item_type):
                    return ProductionMaterial(new_identification_str, item.production_material_id, item.size,
                                              new_item_type)

        parts[-1] = str(int(3))
        new_identification_str = ".".join(parts)
        new_item_type = ItemType(3)
        return ProductionMaterial(new_identification_str, item.production_material_id, item.size, new_item_type)


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

    def get_producing_production_material_on_machine(self, machine: Machine):
        for item in machine.machine_storage.storage_before_process.items:
            for processing_order in machine.processing_list:
                if item.production_material_id == processing_order.order.product.product_id:
                    machine.producing_production_material = item

    def check_if_order_is_finished(self, machine: Machine, new_item: ProductionMaterial):
        """If no more material need to be produced for an order -> remove this order from machine.process_material_list
        and machine.processing_list"""

        for process_material in machine.process_material_list[:]:
            if new_item.identification_str == process_material.produceing_material.identification_str:

                # remove process_material from machine.processing_material_list
                if process_material.quantity_producing == 0:
                    machine.process_material_list.remove(process_material)

                    # remove order from machine.processing_list
                    for processing_order in machine.processing_list[:]:
                        if processing_order.order.product.product_id == new_item.production_material_id:
                            machine.processing_list.remove(processing_order)

    def sort_machine_processing_list(self, machine: Machine):
        """The processing list is sorted according to the following criteria:
        1. If the product is currently being produced, it has the highest sorting priority.
        2. What priority the order has.
        3. How far the value-adding process has progressed."""
        if machine.producing_production_material is not None:
            machine.processing_list.sort(
                key=lambda po: (
                    po.order.product.product_id != machine.producing_production_material.production_material_id,
                    po.priority,
                    -po.step_of_the_process
                )
            )
        else:
            machine.processing_list.sort(
                key=lambda po: (po.priority, -po.step_of_the_process)
            )