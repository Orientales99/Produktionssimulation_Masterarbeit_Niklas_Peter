from datetime import date

from simpy import Store

from src.constant.constant import MachineQuality, ProductGroup, ItemType, MachineStorageStatus, \
    MachineWorkingRobotStatus, MachineProcessStatus, OrderPriority
from src.entity.machine.Process_material import ProcessMaterial
from src.entity.machine.machine import Machine
from src.entity.machine.machine_storage import MachineStorage
from src.entity.machine.machine_working_status import MachineWorkingStatus
from src.entity.machine.processing_order import ProcessingOrder
from src.order_data.order import Order
from src.order_data.product import Product
from src.order_data.production_material import ProductionMaterial
from src.production.base.coordinates import Coordinates


class ConvertDictToMachine:
    def __init__(self, env):
        self.env = env

    def deserialize_complete_machine(self, machine_dict: dict) -> Machine:
        # Extracting basic attributes
        entity_data = machine_dict["entities"][0]["entity_data"]
        size = Coordinates(entity_data["size"]["x"], entity_data["size"]["y"])

        machine_storage = self._rebuild_machine_storage(entity_data["storage"])
        working_status = self._rebuild_working_status(entity_data["working_status"])

        # Extracting quality
        machine_quality = self._rebuild_machine_quality(entity_data["machine_quality"])

        # Rebuilding orders and materials
        processing_orders = self._rebuild_processing_orders(entity_data["Processing Order List"])
        process_materials = self._rebuild_process_materials(entity_data["Process Material List"])

        return Machine(
            machine_type=entity_data["machine_type"],
            identification_number=machine_dict.get("identification_number", 0),
            ##################################################
            machine_quality=machine_quality,
            driving_speed=entity_data["driving_speed"],
            working_speed=entity_data["working_speed"],
            size=size,
            machine_storage=machine_storage,
            working_status=working_status,
            setting_up_time=entity_data["setting_up_time"],
            processing_list=processing_orders,
            process_material_list=process_materials,
            processing_list_queue_length=entity_data["processing_list_queue_length"]
        )

    def _rebuild_machine_storage(self, storage_dict: dict) -> MachineStorage:
        """
        Rebuilds a MachineStorage object from a dictionary.
        This method creates the 'storage_before_process' and 'storage_after_process' from the provided dictionary.
        """
        # Rebuild the 'storage_before_process'
        contained_units = storage_dict["before_process"]["Contained Units"]
        capacity_store_before_process = storage_dict["before_process"]["Max Capacity"]
        if contained_units != 0:
            for identification_str in storage_dict["before_process"]["Loaded Products"]:
                production_material = self._rebuild_production_material_from_ident_str(identification_str)

        storage_before_process = Store(self.env, capacity=capacity_store_before_process)

        # Rebuild the 'storage_after_process'
        contained_units = storage_dict["after_process"]["Contained Units"]
        capacity_store_after_process = storage_dict["after_process"]["Max Capacity"]
        if contained_units != 0:
            for identification_str in storage_dict["after_process"]["Loaded Products"]:
                production_material = self._rebuild_production_material_from_ident_str(identification_str)

        storage_after_process = Store(self.env, capacity=capacity_store_after_process)

        return MachineStorage(storage_before_process, storage_after_process)

    def _rebuild_production_material_from_ident_str(self, ident_str: str) -> ProductionMaterial:
        """
        Rebuilds a ProductionMaterial object from its identification string.
        Extracts information like ProductGroup, ItemType, and Size.
        """
        # Example of how to split the identification string
        parts = ident_str.split(".")

        product_group = ProductGroup[parts[1]]  # z.B. 'FIFTEEN' → ProductGroup.FIFTEEN
        item_type = int(parts[2])

        try:
            # Convert the ProductGroup to the enum
            production_material_id = product_group
        except KeyError:
            raise ValueError(f"Invalid ProductGroup in identification string: {product_group}")

        try:
            # Convert the ItemType to the enum
            item_type = ItemType(item_type)
        except ValueError:
            raise ValueError(f"Invalid ItemType in identification string: {item_type}")

        # Assuming a fixed size (or it could be part of the identification string if needed)
        size = Coordinates(x=1, y=1)  # Example size; adjust if necessary

        return ProductionMaterial(
            identification_str=ident_str,
            production_material_id=production_material_id,
            size=size,
            item_type=item_type
        )

    def _rebuild_machine_quality(self, quality_str: str) -> MachineQuality:
        # Rebuilds the MachineQuality from a dictionary
        if quality_str == "NEW_MACHINE":
            return MachineQuality.NEW_MACHINE
        elif quality_str == "OLD_MACHINE":
            return MachineQuality.OLD_MACHINE
        else:
            raise Exception("MachineQuality doesn't exist")


    def _rebuild_working_status(self, status_dict: dict) -> MachineWorkingStatus:
        return MachineWorkingStatus(
            process_status=self._rebuild_process_status(status_dict["process_status"]),
            working_robot_status=self._rebuild_working_robot_status(status_dict["working_robot_status"]),
            storage_status=self._rebuild_storage_status(status_dict["storage_status"]),
            working_on_status=status_dict["working_on_status"],
            producing_item=status_dict["producing_item"],
            producing_production_material=self._rebuild_production_material_from_ident_str(
                status_dict["producing_production_material"]),
            waiting_for_arriving_of_tr=status_dict["waiting_for_arriving_of_tr"]
        )

    def _rebuild_process_status(self, process_status_str: str) -> MachineProcessStatus:
        return MachineProcessStatus(process_status_str)

    def _rebuild_working_robot_status(self, working_robot_status_str: str) -> MachineWorkingRobotStatus:
        return MachineWorkingRobotStatus(working_robot_status_str)

    def _rebuild_storage_status(self, storage_status_str: str) -> MachineStorageStatus:
        return MachineStorageStatus(storage_status_str)

    def _rebuild_processing_orders(self, processing_list_dict: list) -> list[ProcessingOrder]:
        return [self._rebuild_processing_order(po) for po in processing_list_dict]

    def _rebuild_processing_order(self, po_dict: dict) -> ProcessingOrder:
        # Rebuilds the ProcessingOrder from a dictionary
        return ProcessingOrder(
            order=self._rebuild_order(po_dict.get("order", {})),
            step_of_the_process=po_dict.get("step_of_the_process", 0),
            priority=po_dict.get("priority", 0)
        )

    def _rebuild_order(self, order_dict: dict) -> Order:
        """
        Rebuilds an Order object from a dictionary, properly handling all complex attributes
        like Product, OrderPriority, and the attributes related to production steps.
        """
        # Extracting basic information for Order
        product_data = order_dict.get("product", {})
        product = self._rebuild_product(product_data)

        order_date = order_dict["order_date"]
        if isinstance(order_date, str):
            order_date = self._parse_date(order_date)  # Assuming this method parses the date string to a date object

        priority_str = order_dict.get("priority", "STANDARD_ORDER_1")
        priority = OrderPriority[
            priority_str] if priority_str in OrderPriority.__members__ else OrderPriority.STANDARD_ORDER_1

        daily_manufacturing_sequence = order_dict.get("daily_manufacturing_sequence", None)

        return Order(
            product=product,
            number_of_products_per_order=order_dict.get("number_of_products_per_order", 0),
            order_date=order_date,
            priority=priority,
            daily_manufacturing_sequence=daily_manufacturing_sequence
        )

    def _rebuild_product(self, product_data: dict) -> Product:
        """
        Rebuilds the Product object from a dictionary.
        """
        product_id_str = product_data.get("product_id", "")
        product_id = ProductGroup[product_id_str] if product_id_str in ProductGroup.__members__ else ProductGroup.ONE

        size_data = product_data.get("size", {})
        size = Coordinates(x=size_data.get("x", 0), y=size_data.get("y", 0))

        item_type_str = product_data.get("item_type")

        # Extracting processing steps and times from product_data
        processing_data = product_data.get("processing_steps", {})
        processing_step_1 = processing_data.get("processing_step_1", None)
        processing_time_step_1 = processing_data.get("processing_time_step_1", None)

        processing_step_2 = processing_data.get("processing_step_2", None)
        processing_time_step_2 = processing_data.get("processing_time_step_2", None)

        processing_step_3 = processing_data.get("processing_step_3", None)
        processing_time_step_3 = processing_data.get("processing_time_step_3", None)

        processing_step_4 = processing_data.get("processing_step_4", None)
        processing_time_step_4 = processing_data.get("processing_time_step_4", None)

        return Product(
            product_id=product_id,
            size=size,
            item_type=item_type_str,
            required_product_type_step_1=None,  # Or set from some other logic
            processing_step_1=processing_step_1,
            processing_time_step_1=processing_time_step_1,
            required_product_type_step_2=None,
            processing_step_2=processing_step_2,
            processing_time_step_2=processing_time_step_2,
            required_product_type_step_3=None,
            processing_step_3=processing_step_3,
            processing_time_step_3=processing_time_step_3,
            required_product_type_step_4=None,
            processing_step_4=processing_step_4,
            processing_time_step_4=processing_time_step_4
        )

    def _parse_date(self, date_str: str) -> date:
        """
        Helper method to parse date strings into actual date objects.
        """
        from datetime import datetime
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    def _rebuild_process_materials(self, process_material_list: list) -> list[ProcessMaterial]:
        return [self._rebuild_process_material(pm) for pm in process_material_list]

    def _rebuild_process_material(self, pm_dict: dict) -> ProcessMaterial:
        # Rebuilds the ProcessMaterial from a dictionary
        return ProcessMaterial(
            required_material=self._rebuild_production_material_from_ident_str(pm_dict.get("required_material", "")),
            quantity_required=pm_dict.get("quantity_required", 0),
            producing_material=self._rebuild_production_material_from_ident_str(pm_dict.get("producing_material", "")),
            quantity_producing=pm_dict.get("quantity_producing", 0),
            required_material_on_tr_for_delivery=pm_dict.get("required_material_on_tr_for_delivery", 0)
        )
