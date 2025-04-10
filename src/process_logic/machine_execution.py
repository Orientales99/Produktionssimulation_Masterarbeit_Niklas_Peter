from src.constant.constant import ItemType, OrderPriority
from src.entity.machine import Machine
from src.entity.processing_order import ProcessingOrder
from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial
from src.process_logic.manufacturing_plan import ManufacturingPlan


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

                    if item.production_material_id != machine.producing_production_material:
                        yield self.env.timeout(machine.setting_up_time)  # Umrüstzeit
                        new_product_produced = True
                        self.machine_manager.get_producing_production_material_on_machine(machine)

                    machine.is_working = True
                    input_store.items.remove(item)
                    # yield self.env.timeout(working_speed)
                    yield self.env.timeout(0)
                    new_item = self.machine_manager.create_new_item_after_process(item)
                    yield output_store.put(new_item)
                    self.reduce_producing_material_by_one(machine, new_item)
                    self.machine_manager.check_if_order_is_finished(machine, new_item)

                    if new_product_produced is True:
                        self.give_order_to_next_machine(new_item, machine)
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
            if new_item.identification_str == process_material.produceing_material.identification_str:
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
        for processing_order in machine.processing_list:
            if new_item.production_material_id == processing_order.order.product.product_id:

                # get processing step of the material
                parts = new_item.identification_str.rsplit(".", 1)
                parts[1] = int(parts[-1])

                if parts[1] == 1:
                    identification_str_shortest_que_time = self.get_shortest_que_time_for_machine_type(
                        2)  # 2 -> because it is processing step 2 if ProductionMaterial.1 is required
                    self.append_existing_order(identification_str_shortest_que_time, processing_order.order, 2)

                elif parts[1] == 2:
                    identification_str_shortest_que_time = self.get_shortest_que_time_for_machine_type(3)
                    self.append_existing_order(identification_str_shortest_que_time, processing_order.order, 3)

                elif parts[1] == 3:
                    identification_str_shortest_que_time = self.get_shortest_que_time_for_machine_type(4)
                    self.append_existing_order(identification_str_shortest_que_time, processing_order.order, 4)

    def get_shortest_que_time_for_machine_type(self, executing_machine_type: int) -> str:
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
