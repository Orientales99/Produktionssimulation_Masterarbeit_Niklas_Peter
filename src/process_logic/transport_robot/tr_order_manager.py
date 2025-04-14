from src.constant.constant import TransportRobotStatus
from src.entity.machine.Process_material import ProcessMaterial
from src.entity.machine.machine import Machine
from src.entity.source import Source
from src.entity.transport_robot.transport_order import TransportOrder
from src.entity.transport_robot.transport_robot import TransportRobot
from src.order_data.production_material import ProductionMaterial
from src.process_logic.transport_robot.transport_request import TransportRequest
from src.production.store_manager import StoreManager


class TrOrderManager:
    transport_request_list: list[TransportRequest]

    def __init__(self, simulation_environment, manufacturing_plan, machine_manager):
        self.env = simulation_environment
        self.manufacturing_plan = manufacturing_plan

        self.machine_manager = machine_manager

        self.store_manager = StoreManager(self.env)

        self.tr_list = self.manufacturing_plan.production.tr_list
        self.machine_list = self.manufacturing_plan.production.machine_list

    def create_transport_request_list_from_machines(self):
        """Creates a new list of TransportRequest objects for each machine.
            If this method is called, the list gets reset and a new list is created.
            """
        self.transport_request_list = []

        for machine in self.machine_list:
            self.machine_manager.sort_machine_processing_list(machine)

            if machine.waiting_for_arriving_of_tr is False:
                if machine.is_working is True or machine.waiting_for_arriving_of_wr is True:
                    transport_request_bring = self.get_transport_request_if_material_is_required(machine)
                    transport_request_take = self.get_transport_request_if_storage_after_process_is_full(machine)

                    if transport_request_bring is not None:
                        self.transport_request_list.append(transport_request_bring)

                    if transport_request_take is not None:
                        self.transport_request_list.append(transport_request_take)

        self.remove_duplicate_transport_requests()
        self.sort_transport_requests_list()
        print(self.transport_request_list)

    def get_transport_request_if_material_is_required(self, machine) -> TransportRequest | None:
        """If more than 50 units are in the storage after the process of a machine. Find the Pick Up station for
        the required material and get a TransportRequest"""

        if len(machine.machine_storage.storage_before_process.items) < 50:
            processing_order = machine.processing_list[0]
            process_material = machine.process_material_list[0]

            pick_up_station = self.get_pick_up_station(process_material)

            return TransportRequest(pick_up_station, machine, processing_order, process_material)

        return

    def get_transport_request_if_storage_after_process_is_full(self, machine) -> TransportRequest | None:
        """If more than 50 units are in the storage after the process of a machine.
        ItemType.value == 4 (FINAL_PRODUCT_PACKED) the TR has to Transport the material to Sink.
        Otherwise, loop machine_list and find the machine with the same required Material in storage_before_process or
        process_material_list """

        if len(machine.machine_storage.storage_after_process.items) > 50:
            production_material = self.store_manager.get_most_common_product_in_store(
                machine.machine_storage.storage_after_process)
            if production_material.item_type.value == 4:
                for priority_index, process_material in enumerate(machine.process_material_list):
                    if process_material.required_material == production_material:
                        processing_order = machine.processing_list[priority_index]

                        sink_coordinates = self.manufacturing_plan.production.sink_coordinates
                        sink_cell = self.manufacturing_plan.production.get_cell(sink_coordinates)
                        sink = sink_cell.placed_entity

                        return TransportRequest(machine, sink, processing_order, process_material)

            for unload_destination_machine in self.machine_list:
                for priority_index, process_material in enumerate(unload_destination_machine.process_material_list):
                    if process_material.required_material == production_material:
                        processing_order = unload_destination_machine.processing_list[priority_index]
                        return TransportRequest(machine, unload_destination_machine, processing_order, process_material)

        return

    def get_pick_up_station(self, request_material: ProcessMaterial) -> Machine | Source | bool:
        """Determines the pickup station (Machine or Source) for the requested material.
        If the item_type_value of required material is 0 (RAW MATERIAL) the pick_up_station is Source. Otherwise,
        loop machine_list and find the machine with the same required Material in storage_after_process or
        process_material_list."""
        stored_item_list: list[ProductionMaterial]

        if request_material.required_material.item_type.value == 0:
            source_coordinates = self.manufacturing_plan.production.source_coordinates
            source_cell = self.manufacturing_plan.production.get_cell(source_coordinates)
            return source_cell.placed_entity

        else:
            for machine in self.machine_list:
                stored_item_list = machine.machine_storage.storage_after_process.items
                for items in stored_item_list:
                    if items.identification_str == request_material.required_material.identification_str:
                        return machine
                if machine.process_material_list[
                    0].producing_material.identification_str == request_material.required_material.identification_str:
                    return machine

        raise Exception(f"{request_material.required_material.identification_str} cannot be found in the production")

    def remove_duplicate_transport_requests(self):
        """
        Removes duplicate TransportRequest entries from self.transport_request_list,
        if both destination_pick_up.identification_str and
        destination_unload.identification_str are identical.
        """
        unique_requests = []
        seen_pairs = set()

        for request in self.transport_request_list:
            pair = (
                request.destination_pick_up.identification_str,
                request.destination_unload.identification_str
            )
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                unique_requests.append(request)

        self.transport_request_list = unique_requests

    def sort_transport_requests_list(self):
        """
        Sorts self.list_transport_request with the following priority:
        1. The transport is currently being processed on the assigned machine.
        2. Order priority.
        3. Step of the process (descending).
        4. Daily manufacturing sequence (ascending)."""

        self.transport_request_list.sort(
            key=lambda tr: (
                not (tr.destination_unload.producing_production_material is not None and
                     tr.destination_unload.producing_production_material.production_material_id ==
                     tr.processing_order.order.product.product_id),
                tr.processing_order.priority,
                -tr.processing_order.step_of_the_process,
                tr.processing_order.order.daily_manufacturing_sequence if
                tr.processing_order.order.daily_manufacturing_sequence is not None else float(
                    'inf')
            )
        )

    def every_idle_tr_get_order(self):
        for tr in self.tr_list:
            self.allocate_order_to_tr(tr)

    def allocate_order_to_tr(self, tr: TransportRobot):
        if tr.working_status.status == TransportRobotStatus.IDLE:
            # get variables
            transport_request = self.transport_request_list[0]
            unload_destination = transport_request.destination_unload
            pick_up_destination = transport_request.destination_pick_up
            transporting_material = transport_request.process_material.required_material
            quantity = self.calculate_order_quantity(tr, transport_request)

            # get transport order for tr
            tr.transport_order = TransportOrder(unload_destination, pick_up_destination, transporting_material, quantity)

            # change list & entity status
            tr.working_status.status = TransportRobotStatus.MOVING_TO_PICKUP
            self.transport_request_list.remove(transport_request)
            if isinstance(pick_up_destination, Machine):
                pick_up_destination.waiting_for_arriving_of_tr = True

            if isinstance(unload_destination, Machine):
                unload_destination.waiting_for_arriving_of_tr = True

    def calculate_order_quantity(self, tr: TransportRobot, transport_request: TransportRequest) -> int:
        """Returns the max transporting quantity. Limited by the required material, transporting capacity of tr and
         capacity of the requesting machine."""
        quantity = transport_request.process_material.quantity_required

        if quantity > tr.material_store.capacity:
            quantity = tr.material_store.capacity

        if isinstance(transport_request.destination_unload, Machine):
            empty_space_in_store = self.store_manager.count_empty_space_in_store(
                transport_request.destination_unload.machine_storage.storage_before_process)
            if quantity > empty_space_in_store:
                quantity = empty_space_in_store

        return quantity



    def get_driving_speed_per_cell(self):
        return int(self.tr_list[0].driving_speed)

    def get_loading_speed(self):
        return int(self.tr_list[0].loading_speed)
