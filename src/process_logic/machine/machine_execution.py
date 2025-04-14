from src.entity.machine.Process_material import ProcessMaterial
from src.entity.machine.machine import Machine
from src.entity.machine.processing_order import ProcessingOrder
from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial


class MachineExecution:
    def __init__(self, env, manufacturing_plan, machine_manager):
        self.env = env
        self.manufacturing_plan = manufacturing_plan
        self.machine_manager = machine_manager

    def run_machine_production(self, machine: Machine):
        working_speed = int(machine.working_speed)
        new_product_produced = False
        while True:
            if machine.working_robot_on_machine:
                input_store = machine.machine_storage.storage_before_process
                output_store = machine.machine_storage.storage_after_process
                item = self.check_processing_list_input_store(machine)

                if item is not False:

                    if machine.producing_production_material is None \
                            or item.production_material_id != machine.producing_production_material.production_material_id:
                        yield self.env.timeout(machine.setting_up_time)  # Umrüstzeit
                        new_product_produced = True
                        self.machine_manager.get_producing_production_material_on_machine(machine)

                    machine.is_working = True
                    input_store.items.remove(item)
                    # yield self.env.timeout(working_speed)
                    # yield self.env.timeout(0)

                    new_item = self.machine_manager.create_new_item_after_process(machine, item)
                    yield output_store.put(new_item)
                    self.reduce_producing_material_by_one(machine, new_item)

                    self.machine_manager.check_if_order_is_finished(machine, new_item)

                    if new_product_produced is True:
                        self.give_order_to_next_machine(new_item, machine)

                        print(f"{machine.identification_str}: {machine.processing_list}")
                        # self.manufacturing_plan.get_required_material_for_every_machine()
                        new_product_produced = False
                else:
                    # Wenn kein Produkt da, kurz warten und neu prüfen
                    machine.is_working = False
                    yield self.env.timeout(1)
            else:
                machine.is_working = False
                # Kein WR zugewiesen → warten und später wieder prüfen
                yield self.env.timeout(1)

    def reduce_producing_material_by_one(self, machine: Machine, new_item: ProductionMaterial):
        for process_material in machine.process_material_list:
            if new_item.identification_str == process_material.producing_material.identification_str:
                process_material.quantity_producing -= 1

    def check_processing_list_input_store(self, machine: Machine) -> ProductionMaterial | bool:
        """ Checks if the machine's input store contains an item matching any order in the processing list.
            Returns: Matching item if found, else None."""
        for processing_order in machine.processing_list:
            for item in machine.machine_storage.storage_before_process.items:
                if item.production_material_id == processing_order.order.product.product_id:
                    return item

        return False

    def give_order_to_next_machine(self, new_item: ProductionMaterial, machine: Machine):
        """Takes the item and gives the order to the next machine."""
        executing_machine_type = None
        step_of_the_process = None

        for processing_order in machine.processing_list:
            if new_item.production_material_id == processing_order.order.product.product_id:
                if processing_order.order.product.required_product_type_step_1 == new_item:
                    executing_machine_type = processing_order.order.product.processing_step_1
                    step_of_the_process = 1

                if processing_order.order.product.required_product_type_step_2 == new_item:
                    executing_machine_type = processing_order.order.product.processing_step_2
                    step_of_the_process = 2

                if processing_order.order.product.required_product_type_step_3 == new_item:
                    executing_machine_type = processing_order.order.product.processing_step_3
                    step_of_the_process = 3

                if processing_order.order.product.required_product_type_step_4 == new_item:
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
        machine_type_list = self.manufacturing_plan.production.service_entity.get_quantity_per_machine_types_list()

        for machine_type, number_of_machines_in_production in machine_type_list:
            if executing_machine_type == machine_type:
                identification_str_shortest_que_time = self.manufacturing_plan.get_machine_str_with_shortest_queue_time(
                    machine_type,
                    number_of_machines_in_production)
                return identification_str_shortest_que_time

    def append_existing_order(self, identification_str_shortest_que_time: str, order: Order, step_of_the_process: int):
        """takes the str from the machine with the shortest_que_time and gives it the new order"""
        for cell in self.manufacturing_plan.production.entities_located[identification_str_shortest_que_time]:
            new_cell = self.manufacturing_plan.production.find_cell_in_production_layout(cell)
            priority = max(0, order.priority.value - step_of_the_process)

            processing_order = ProcessingOrder(order, step_of_the_process, priority)
            if processing_order not in new_cell.placed_entity.processing_list:
                new_cell.placed_entity.processing_list.append(processing_order)
                self.manufacturing_plan.process_list_for_every_machine.append((cell.placed_entity, processing_order))
                self.append_existing_process_material_list(cell.placed_entity, processing_order)
                self.machine_manager.sort_machine_processing_list(cell.placed_entity)

    def append_existing_process_material_list(self, machine: Machine, processing_order: ProcessingOrder):
        """append required material and quantity based on the processing_list"""

        # required material
        data_processing_step = self.machine_manager.get_data_of_processing_step_for_machine(processing_order.order,
                                                                                            machine)
        required_material = data_processing_step[0]
        quantity_of_necessary_material = processing_order.order.number_of_products_per_order
        # producing material
        producing_material = self.machine_manager.create_new_item_after_process(machine, required_material)
        quantity_of_producing_material = quantity_of_necessary_material
        machine.process_material_list.append(ProcessMaterial(required_material, quantity_of_necessary_material,
                                                             producing_material,
                                                             quantity_of_producing_material))
