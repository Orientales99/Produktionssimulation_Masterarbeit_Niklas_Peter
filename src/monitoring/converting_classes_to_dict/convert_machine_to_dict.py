from collections import defaultdict

from simpy import Store

from src.entity.machine.Process_material import ProcessMaterial
from src.entity.machine.machine import Machine
from src.entity.machine.processing_order import ProcessingOrder
from src.production.store_manager import StoreManager


class ConvertMachineToDict:
    store_manager: StoreManager

    def __init__(self, store_manager):
        self.store_manager = store_manager

    def serialize_complete_machine(self, machine: Machine) -> dict:
        products_in_before_process_store = self.store_manager.get_dict_number_of_products_in_store(
            machine.machine_storage.storage_before_process)
        products_in_after_process_store = self.store_manager.get_dict_number_of_products_in_store(
            machine.machine_storage.storage_after_process)
        processing_order_list = self.get_dict_processing_order_list(machine.processing_list)
        process_material_list = self.get_str_process_material_list(machine.process_material_list)

        return {
            "machine_type": machine.machine_type,
            "identification_str": machine.identification_str,
            "machine_quality": machine.machine_quality.name,
            "driving_speed": machine.driving_speed,
            "working_speed": machine.working_speed,
            "working_speed_deviation_in_percent": machine.working_speed_deviation * 100,
            "setting_up_time": machine.setting_up_time,
            "processing_list_queue_length": machine.processing_list_queue_length,
            "size": {
                "x": machine.size.x,
                "y": machine.size.y
            },
            "working_status": {
                "process_status": machine.working_status.process_status.value,
                "working_robot_status": machine.working_status.working_robot_status.value,
                "storage_status": machine.working_status.storage_status.value,
                "working_on_status": machine.working_status.working_on_status,
                "producing_item": machine.working_status.producing_item,
                "producing_production_material": (
                    machine.working_status.producing_production_material.identification_str
                    if machine.working_status.producing_production_material else None
                ),
                "waiting_for_arriving_of_tr": machine.working_status.waiting_for_arriving_of_tr
            },
            "storage": {
                "before_process": {
                    "Max Capacity": machine.machine_storage.storage_before_process.capacity,
                    "Contained Units": len(machine.machine_storage.storage_before_process.items),
                    "Loaded Products": products_in_before_process_store
                },
                "after_process": {
                    "Max Capacity": machine.machine_storage.storage_after_process.capacity,
                    "Contained Units": len(machine.machine_storage.storage_after_process.items),
                    "Loaded Products": products_in_after_process_store
                }
            },
            "Processing Order List": processing_order_list,
            "Process Material List": process_material_list

        }

    def get_dict_processing_order_list(self, order_list: list[ProcessingOrder]) -> list[dict]:
        """
        Converts a list of ProcessingOrder objects into a list of dictionaries.
        """
        dict_list = []

        for processing_order in order_list:
            order = processing_order.order

            order_dict = {
                "product_identification": order.product.identification_str,
                "order_date": str(order.order_date),  # Convert date to string for JSON compatibility
                "number_of_products": order.number_of_products_per_order,
                "priority": order.priority.name,
                "step_of_process": processing_order.step_of_the_process,
                "daily_manufacturing_sequence": order.daily_manufacturing_sequence,
            }

            dict_list.append(order_dict)

        return dict_list

    def get_str_process_material_list(self, process_material_list: list[ProcessMaterial]) -> list[dict]:
        """Get a dict with different RequiredMaterial.identification_str and counts their quantity."""
        if not process_material_list:
            return []

        process_materials_data = []

        for process_material in process_material_list:
            entry = {
                "required_material": {
                    "id": process_material.required_material.identification_str,
                    "quantity": process_material.quantity_required
                },
                "producing_material": {
                    "id": process_material.producing_material.identification_str,
                    "quantity": process_material.quantity_producing
                },
                "required_material_on_tr_for_delivery": process_material.required_material_on_tr_for_delivery
            }
            process_materials_data.append(entry)

        return process_materials_data


