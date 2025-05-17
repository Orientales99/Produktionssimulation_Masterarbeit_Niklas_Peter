import copy

from src.constant.constant import ItemType
from src.entity.machine.Process_material import ProcessMaterial
from src.entity.machine.machine import Machine
from src.entity.machine.processing_order import ProcessingOrder
from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial
from src.process_logic.machine.machine_manager import MachineManager
from src.production.base.coordinates import Coordinates
from src.production.production import Production


class ObjectMaterialFlowMatrix:
    movable_machine_list: list[Machine]

    object_material_flow_matrix: dict[
        str, dict[str, int]]  # Material_flow between one Object (str = identification_str)
    # and every other Object
    # (str = identification_str, int = Material_flow quantity)

    number_of_wr_in_production: int

    def __init__(self, production: Production, machine_manager: MachineManager):
        self.production = production
        self.machine_manager = machine_manager
        self.movable_machine_list = []
        self.number_of_wr_in_production = len(self.production.wr_list)

    def start_creating_material_flow_matrix(self):
        self.save_every_movable_machine_in_production()

    def save_every_movable_machine_in_production(self):
        """Creating a copy of the movable machine objects in the production"""
        entity_keys = self.production.entities_located.keys()
        for key in entity_keys:
            key_cell_list = self.production.entities_located[key]
            cell = key_cell_list[0]

            if isinstance(cell.placed_entity, Machine):
                if cell.placed_entity.driving_speed != 0:
                    copied_machine = copy.deepcopy(cell.placed_entity)
                    self.movable_machine_list.append(copied_machine)

    def assigning_process_steps_of_products_to_machine(self):
        sorted_process_order_list = self.get_sort_process_order_list()
        for i, (machine, order) in enumerate(sorted_process_order_list):
            if i >= self.number_of_wr_in_production:
                break

            self.give_order_to_next_machine(machine.process_material_list[0].producing_material, machine)


#####################################################################################################

    def get_sort_process_order_list(self) -> list[tuple[Machine, ProcessingOrder]]:
        """
        Delete orders when machine.process_material_list[0].quantity_producing == 0 ist.
        Sort list [machine, processing_order(Order, step_of_the_process_priority)].
         1. priority
         2. step of the process
         3. daily manufacturing_sequence
         """
        list_of_processes_for_every_machine = self.get_process_list_of_every_machine()

        list_of_processes_for_every_machine = [(machine, order) for machine, order in
                                               list_of_processes_for_every_machine
                                               if machine.process_material_list and machine.process_material_list[
                                                   0].quantity_producing != 0]

        sorted_list_of_processes = sorted(
            list_of_processes_for_every_machine,
            key=lambda x: (x[1].order.priority.value,
                           - x[1].step_of_the_process,
                           x[1].order.daily_manufacturing_sequence,
                           )
        )
        return sorted_list_of_processes



    def get_process_list_of_every_machine(self) -> list[(Machine, ProcessingOrder)]:
        process_list_for_every_machine: [(Machine, ProcessingOrder)]
        process_list_for_every_machine = []

        for machine in self.movable_machine_list:
            if len(machine.processing_list) > 0:
                process_list_for_every_machine.append((machine, machine.processing_list[0]))

        return process_list_for_every_machine

    def give_order_to_next_machine(self, producing_material: ProductionMaterial, machine: Machine):
        """Takes the item and gives the order to the next machine."""
        executing_machine_type = None
        step_of_the_process = None

        for processing_order in machine.processing_list:
            if producing_material.production_material_id == processing_order.order.product.product_id:
                if processing_order.order.product.required_product_type_step_1 == producing_material:
                    executing_machine_type = processing_order.order.product.processing_step_1
                    step_of_the_process = 1

                if processing_order.order.product.required_product_type_step_2 == producing_material:
                    executing_machine_type = processing_order.order.product.processing_step_2
                    step_of_the_process = 2

                if processing_order.order.product.required_product_type_step_3 == producing_material:
                    executing_machine_type = processing_order.order.product.processing_step_3
                    step_of_the_process = 3

                if processing_order.order.product.required_product_type_step_4 == producing_material:
                    executing_machine_type = processing_order.order.product.processing_step_4
                    step_of_the_process = 4

                if step_of_the_process is not None and executing_machine_type is not None:

                    machine_identification_str_shortest_que_time = self.get_shortest_que_time_for_machine_type(
                        executing_machine_type)
                    if machine_identification_str_shortest_que_time is not None:
                        self.append_existing_order(machine_identification_str_shortest_que_time, processing_order.order,
                                                   step_of_the_process)

    def get_shortest_que_time_for_machine_type(self, executing_machine_type: int) -> str:
        """Get the identification str of the machine with the shortest que time. It is a selection of all
         machine with the same type."""
        machine_type_list = []
        for machine in self.movable_machine_list:
            if machine.machine_type == executing_machine_type:
                machine_type_list.append(machine)

        for machine_type in machine_type_list:
            number_of_machines_in_production = len(machine_type_list)
            if executing_machine_type == machine_type:
                identification_str_shortest_que_time = self.get_machine_str_with_shortest_queue_time(
                    machine_type.machine_type,
                    number_of_machines_in_production)

                return identification_str_shortest_que_time

    def append_existing_order(self, identification_str_shortest_que_time: str, order: Order, step_of_the_process: int):
        """takes the str from the machine with the shortest_que_time and gives it the new order"""
        for machine in self.movable_machine_list:
            if machine.identification_str == identification_str_shortest_que_time:
                priority = max(0, order.priority.value - step_of_the_process)
                processing_order = ProcessingOrder(order, step_of_the_process, priority)

                if processing_order not in machine.processing_list:
                    machine.processing_list.append(processing_order)
                    self.append_existing_process_material_list(machine, processing_order)


    def append_existing_process_material_list(self, machine: Machine, processing_order: ProcessingOrder):
        """append required material and quantity based on the processing_list"""
        # required material
        data_processing_step = self.get_data_of_processing_step_for_machine(processing_order.order,
                                                                                            machine)
        required_material = data_processing_step[0]
        quantity_of_necessary_material = processing_order.order.number_of_products_per_order
        # producing material
        producing_material = self.create_new_item_after_process(machine, required_material)
        quantity_of_producing_material = quantity_of_necessary_material
        machine.process_material_list.append(ProcessMaterial(required_material, quantity_of_necessary_material,
                                                             producing_material,
                                                             quantity_of_producing_material))

    def get_machine_str_with_shortest_queue_time(self, machine_type: int,
                                                 number_of_machines_per_machine_type: int) -> str:
        """Finds the machine with the shortest queue time and returns its identification string.
           If no machine is found, an error is returned."""
        identification_str_shortest_que_time = ""
        total_shortest_que_time = float("inf")

        for identification_number in range(1, number_of_machines_per_machine_type + 1):
            identification_str = f"Ma: {machine_type}, {identification_number}"

            new_cell = self.production.find_cell_in_production_layout(
                self.production.entities_located[identification_str][1])
            machine = new_cell.placed_entity
            shortest_que_time = self.machine_manager.calculating_processing_list_queue_length(machine)

            if shortest_que_time < total_shortest_que_time:
                total_shortest_que_time = shortest_que_time
                identification_str_shortest_que_time = identification_str

        if identification_str_shortest_que_time == "":
            return Exception("Queue time couldn't be calculated. Check if every required machine type is initialised")

        return identification_str_shortest_que_time

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
