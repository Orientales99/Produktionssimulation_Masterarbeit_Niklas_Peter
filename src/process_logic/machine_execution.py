from src.constant.constant import ItemType, OrderPriority
from src.entity.machine import Machine
from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial
from src.process_logic.manufacturing_plan import ManufacturingPlan


class MachineExecution:
    def __init__(self, env, manufacturing_plan):
        self.env = env
        self.manufacturing_plan = manufacturing_plan

    def run_machine_production(self, machine):
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
                        self.get_production_prodution_material_on_machine(machine)

                    machine.is_working = True
                    input_store.items.remove(item)
                    yield self.env.timeout(working_speed)
                    new_item = self.create_new_item_after_process(item)
                    yield output_store.put(new_item)

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

    def get_production_prodution_material_on_machine(self, machine: Machine):
        for item in machine.machine_storage.storage_before_process.items:
            for order, quantity in machine.processing_list:
                if item.production_material_id == order.product.product_id:
                    machine.producing_production_material = item

    def check_processing_list_input_store(self, machine: Machine) -> ProductionMaterial | bool:
        """ Checks if the machine's input store contains an item matching any order in the processing list.
            Returns: Matching item if found, else None."""
        for item in machine.machine_storage.storage_before_process.items:
            for order, quantity in machine.processing_list:
                if item.production_material_id == order.product.product_id:
                    return item
        return False

    def create_new_item_after_process(self, item: ProductionMaterial) -> ProductionMaterial:
        """Creating a new ProductionMaterial, identification_str gets an update (ex:# Example: ProductGroup.SEVEN.0 ->
         Example: ProductGroup.SEVEN.1, and item_type (+1).
         Return: new ProductionMaterial"""
        parts = item.identification_str.rsplit(".", 1)
        parts[-1] = str(int(parts[-1]) + 1)
        new_identification_str = ".".join(parts)

        new_item_type = ItemType(item.item_type.value + 1)

        return ProductionMaterial(new_identification_str, item.production_material_id, item.size, new_item_type)

    def give_order_to_next_machine(self, new_item: ProductionMaterial, machine: Machine):
        """Takes the item and gives the order to the next machine."""
        for order, quantity in machine.processing_list:
            if new_item.production_material_id == order.product.product_id:

                # get processing step of the material
                parts = new_item.identification_str.rsplit(".", 1)
                parts[1] = int(parts[-1])

                if parts[1] == 1:
                    identification_str_shortest_que_time = self.get_shortest_que_time_for_machine_type(
                        2)  # 2 -> because it is processing step 2 if ProductionMaterial.1 is required
                    self.decrease_order_priority(order)
                    self.append_existing_order(identification_str_shortest_que_time, order)

                elif parts[1] == 2:
                    identification_str_shortest_que_time = self.get_shortest_que_time_for_machine_type(3)
                    self.decrease_order_priority(order)
                    self.append_existing_order(identification_str_shortest_que_time, order)

                elif parts[1] == 3:
                    identification_str_shortest_que_time = self.get_shortest_que_time_for_machine_type(5)
                    self.decrease_order_priority(order)
                    self.append_existing_order(identification_str_shortest_que_time, order)

    def decrease_order_priority(self, order):
        """decrease the priority_number but increasing the importance of the Order"""
        priorities = list(OrderPriority)
        current_index = priorities.index(order.priority)
        new_index = max(0, current_index - 1)
        order.priority = priorities[new_index]

    def get_shortest_que_time_for_machine_type(self, executing_machine_type: int) -> str:
        machine_type_list = self.manufacturing_plan.production.service_entity.get_quantity_per_machine_types_list()

        for machine_type, number_of_machines_in_production in machine_type_list:
            if executing_machine_type == machine_type:
                identification_str_shortest_que_time = self.manufacturing_plan.get_machine_str_with_shortest_queue_time(
                    machine_type,
                    number_of_machines_in_production)
                return identification_str_shortest_que_time

    def append_existing_order(self, identification_str_shortest_que_time: str, order: Order):
        """takes the str from the machine with the shortest_que_time and gives it the new order"""
        for cell in self.manufacturing_plan.production.entities_located[identification_str_shortest_que_time]:
            new_cell = self.manufacturing_plan.production.find_cell_in_production_layout(cell)
            if (order, 1) not in new_cell.placed_entity.processing_list:
                new_cell.placed_entity.processing_list.append((order, 1))
                self.manufacturing_plan.process_list_for_every_machine.append((cell.placed_entity, order, 1))
