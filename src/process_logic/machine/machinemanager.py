from src.constant.constant import MachineQuality, ItemType, MachineWorkingRobotStatus
from src.entity.machine.machine import Machine
from src.entity.machine.Process_material import ProcessMaterial
from src.entity.working_robot.working_robot import WorkingRobot
from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial


class MachineManager:
    machine_list: list[Machine]
    list_full_store_after_process = list[Machine]

    def __init__(self, production, store_manager):
        self.production = production
        self.machine_list = self.production.machine_list
        self.store_manager = store_manager

        self.list_full_store_after_process = []
        self.material_transport_request_list = []

    def calculating_processing_list_queue_length(self, machine: Machine):
        if len(machine.processing_list) != 0:
            machine.processing_list_queue_length = float(0)
            for processing_order in machine.processing_list:
                number_of_required_products = processing_order.order.number_of_products_per_order
                time_to_process_one_product = self.get_time_to_process_one_product(processing_order.order,
                                                                                   processing_order.step_of_the_process)
                if processing_order.order.product != machine.working_status.producing_production_material:
                    machine.processing_list_queue_length += (
                                                                    int(number_of_required_products) * time_to_process_one_product) + \
                                                            machine.setting_up_time
                elif processing_order.order.product == machine.working_status.producing_production_material:
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

                if (product.required_product_type_step_4 is not None and
                        ItemType.FINAL_PRODUCT_PACKED == new_item_type):
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

    def check_if_order_is_finished(self, machine: Machine, new_item: ProductionMaterial) -> bool:
        """If no more material need to be produced for an order
        Return True -> order is finished with producing
        Return False -> order is not finished"""

        for process_material in machine.process_material_list[:]:
            if new_item.identification_str == process_material.producing_material.identification_str:

                # remove process_material from machine.processing_material_list
                if process_material.quantity_producing == 0:
                    return True
        return False

    def remove_processing_order_from_machine(self, machine: Machine, new_item: ProductionMaterial) -> bool:
        """"If no more material need to be produced for an order and no material is in output store to be picked up
        -> remove this order from machine.process_material_list and machine.processing_list"""
        if self.store_manager.count_number_of_one_product_type_in_store(machine.machine_storage.storage_after_process,
                                                                        new_item) == 0:

            for process_material in machine.process_material_list[:]:
                if new_item.identification_str == process_material.producing_material.identification_str:

                    # remove process_material from machine.processing_material_list
                    if process_material.quantity_producing == 0:
                        for processing_order in machine.processing_list[:]:
                            if processing_order.order.product.product_id == new_item.production_material_id:
                                machine.processing_list.remove(processing_order)

    def sort_machine_processing_list(self, machine: Machine):
        """The processing list is sorted according to the following criteria:
        1. If the product is currently being produced, it has the highest sorting priority or the storage is filled with the product of the first order.
        2. What priority the order has.
        3. How far the value-adding process has progressed.
        If the machine is waiting for a TR and WR, keep the first item at the top."""

        first_before_sorting = machine.processing_list[0] if machine.processing_list else None

        if machine.working_status.producing_production_material is not None:
            machine.processing_list.sort(
                key=lambda po: (
                    po.order.product.product_id != machine.working_status.producing_production_material.production_material_id,
                    po.priority,
                    -po.step_of_the_process
                )
            )
        else:
            machine.processing_list.sort(
                key=lambda po: (po.priority, -po.step_of_the_process)
            )

        # Restore the original first item if waiting for a TR or WR
        if machine.working_status.waiting_for_arriving_of_tr or \
                machine.working_status.working_robot_status == MachineWorkingRobotStatus.WAITING_WR or \
                machine.working_status.working_robot_status == MachineWorkingRobotStatus.WR_PRESENT or \
                len(machine.machine_storage.storage_before_process.items) != 0:
            machine.processing_list.remove(first_before_sorting)
            machine.processing_list.insert(0, first_before_sorting)

        self.sort_process_material_list_by_processing_list(machine)

    def sort_process_material_list_by_processing_list(self, machine: Machine) -> None:
        """
        Sorts the machine.process_material_list based on the order of
        machine.processing_list, matching by product_id.
        """

        id_to_material = {process_material.producing_material.production_material_id: process_material
                          for process_material in machine.process_material_list}

        sorted_process_material_list = [id_to_material[processing_order.order.product.product_id]
                                        for processing_order in machine.processing_list
                                        if processing_order.order.product.product_id in id_to_material]

        machine.process_material_list[:] = sorted_process_material_list

    def get_wr_working_on_machine(self, machine: Machine) -> WorkingRobot:
        """Return the Working Robot which is working on the machine"""

        for wr in self.production.wr_list:
            if wr.working_status.working_for_machine == machine:
                return wr
        print(f"get_wr_working_on_machine: No WR is working on {machine.identification_str}")

    def check_required_material_in_storage_before_process(self, machine: Machine, required_material: ProductionMaterial) \
            -> bool:
        """Return True: Enough Material (>= 1) is in storage.
           Return False: 0 Material is in storage before process. """

        input_store = machine.machine_storage.storage_before_process

        number_of_items = self.store_manager.count_number_of_one_product_type_in_store(input_store, required_material)
        if number_of_items > 0:
            return True
        else:
            return False
