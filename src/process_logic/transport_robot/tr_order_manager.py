from src.constant.constant import TransportRobotStatus, MachineWorkingRobotStatus, MachineStorageStatus
from src.entity.intermediate_store import IntermediateStore
from src.entity.machine.Process_material import ProcessMaterial
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_robot.transport_order import TransportOrder
from src.entity.transport_robot.transport_robot import TransportRobot
from src.order_data.production_material import ProductionMaterial
from src.process_logic.transport_robot.transport_request import TransportRequest


class TrOrderManager:
    transport_request_list: list[TransportRequest]
    machine_list: list[Machine]
    intermediate_store_list: list[IntermediateStore]

    def __init__(self, simulation_environment, manufacturing_plan, machine_manager, store_manager):
        self.env = simulation_environment
        self.manufacturing_plan = manufacturing_plan

        self.machine_manager = machine_manager

        self.store_manager = store_manager

        self.tr_list = self.manufacturing_plan.production.tr_list
        self.machine_list = self.manufacturing_plan.production.machine_list
        self.intermediate_store_list = self.manufacturing_plan.production.intermediate_store_list

    def create_transport_request_list_from_machines(self):
        """Creates a new list of TransportRequest objects for each machine.
            If this method is called, the list gets reset and a new list is created.
            """
        self.transport_request_list = []
        transport_request_bring = None

        for machine in self.machine_list:
            self.machine_manager.sort_machine_processing_list(machine)

            if machine.working_status.waiting_for_arriving_of_tr is False:
                if machine.working_status.working_robot_status == MachineWorkingRobotStatus.WAITING_WR or \
                        machine.working_status.working_robot_status == MachineWorkingRobotStatus.WR_PRESENT:
                    if machine.working_status.storage_status == MachineStorageStatus.INPUT_EMPTY:
                        transport_request_bring = self.get_transport_request_if_material_is_required(machine)
                        transport_request_bring = self.remove_transport_request_zero_quantity(transport_request_bring)

                    if transport_request_bring is not None:
                        self.transport_request_list.append(transport_request_bring)

                if machine.working_status.storage_status == MachineStorageStatus.OUTPUT_FULL:
                    transport_request_take = self.get_transport_request_if_storage_after_process_is_filled(machine)
                    if transport_request_take is not None:
                        self.transport_request_list.append(transport_request_take)

        self.remove_duplicate_transport_requests()
        self.sort_transport_requests_list()

    def get_transport_request_if_material_is_required(self, machine) -> TransportRequest | None:
        """Find the Pick Up station for the required material and get a TransportRequest"""

        processing_order = machine.processing_list[0]
        process_material = machine.process_material_list[0]
        pick_up_station = self.get_pick_up_station(process_material)
        if pick_up_station is not False:
            if isinstance(pick_up_station, Machine):
                if len(pick_up_station.machine_storage.storage_after_process.items) >= 1:
                    return TransportRequest(pick_up_station, machine, processing_order, process_material)
            elif isinstance(pick_up_station, Source | IntermediateStore):
                return TransportRequest(pick_up_station, machine, processing_order, process_material)
        return

    def get_transport_request_if_storage_after_process_is_filled(self, machine: Machine) -> TransportRequest | None:
        """ItemType.value == 4 (FINAL_PRODUCT_PACKED) the TR has to Transport the material to Sink.
        Otherwise, loop machine_list and find the machine with the same required Material in storage_before_process or
        process_material_list """

        production_material = self.store_manager.get_most_common_product_in_store(
            machine.machine_storage.storage_after_process)
        if production_material is not None:
            if production_material.item_type.value == 4:
                for priority_index, process_material in enumerate(machine.process_material_list):
                    if process_material.producing_material == production_material:
                        processing_order = machine.processing_list[priority_index]
                        sink_coordinates = self.manufacturing_plan.production.sink_coordinates
                        sink_cell = self.manufacturing_plan.production.get_cell(sink_coordinates)
                        sink = sink_cell.placed_entity
                        return TransportRequest(machine, sink, processing_order, process_material)
            for unload_destination_machine in self.machine_list:
                if len(unload_destination_machine.process_material_list) > 0:
                    process_material = unload_destination_machine.process_material_list[0]
                    if process_material.required_material == production_material:
                        processing_order = unload_destination_machine.processing_list[0]
                        if len(unload_destination_machine.machine_storage.storage_before_process.items) < unload_destination_machine.machine_storage.storage_before_process.capacity:
                            return TransportRequest(machine, unload_destination_machine, processing_order, process_material)

            # assignment to intermediate_store must be revised for multiple stores
            intermediate_store_list = self.manufacturing_plan.production.service_entity.\
                                                                                    generate_intermediate_store_list()
            for intermediate_store in intermediate_store_list:
                intermediate_store_cell_list = self.manufacturing_plan.production.entities_located[
                    intermediate_store.identification_str]
                intermediate_store = intermediate_store_cell_list[0].placed_entity
                for priority_index, process_material in enumerate(machine.process_material_list):
                    if process_material.producing_material == production_material:
                        processing_order = machine.processing_list[priority_index]
                        return TransportRequest(machine, intermediate_store, processing_order, process_material)
        return

    def get_pick_up_station(self, request_material: ProcessMaterial) -> Machine | Source | IntermediateStore | bool:
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

                if len(machine.process_material_list) > 0:
                    if machine.process_material_list[0].producing_material.identification_str == \
                            request_material.required_material.identification_str:
                        return machine
            for intermediate_store in self.intermediate_store_list:
                stored_item_list = intermediate_store.intermediate_store.items
                for items in stored_item_list:
                    if items.identification_str == request_material.required_material.identification_str:
                        return intermediate_store


        return False

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

    def remove_transport_request_zero_quantity(self, transport_request: TransportRequest) -> TransportRequest | None:
        """remove every transport request with the transport quantity of zero"""

        if transport_request is None:
            return None

        if isinstance(transport_request.destination_unload, Machine):
            if transport_request.destination_unload.process_material_list[0].quantity_producing == 0:
                return None
        return transport_request

    def sort_transport_requests_list(self):
        """
        Sorts self.list_transport_request with the following priority:
        1. Order priority.
        2. Step of the process (descending).
        3. Daily manufacturing sequence (ascending)."""

        self.transport_request_list.sort(
            key=lambda tr: (
                tr.processing_order.priority,
                -tr.processing_order.step_of_the_process,
                tr.processing_order.order.daily_manufacturing_sequence if
                tr.processing_order.order.daily_manufacturing_sequence is not None else float(
                    'inf')))

    def every_idle_tr_get_order(self):
        for tr in self.tr_list:
            self.allocate_order_to_tr(tr)

    def allocate_order_to_tr(self, tr: TransportRobot):
        if tr.working_status.status == TransportRobotStatus.IDLE:
            # get variables
            if len(self.transport_request_list) > 0:
                transport_request = self.transport_request_list[0]
                unload_destination = transport_request.destination_unload
                pick_up_destination = transport_request.destination_pick_up
                transporting_material = transport_request.process_material.required_material
                quantity = self.calculate_order_quantity(tr, transport_request)

                if isinstance(unload_destination, Sink | IntermediateStore):
                    transporting_material = pick_up_destination.process_material_list[0].producing_material

                # get transport order for tr
                tr.transport_order = TransportOrder(unload_destination, pick_up_destination, transporting_material,
                                                    quantity)

                # change list & entity status
                tr.working_status.status = TransportRobotStatus.MOVING_TO_PICKUP
                self.transport_request_list.remove(transport_request)
                if isinstance(pick_up_destination, Machine):
                    pick_up_destination.working_status.waiting_for_arriving_of_tr = True

                if isinstance(unload_destination, Machine):
                    unload_destination.working_status.waiting_for_arriving_of_tr = True

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

        if isinstance(transport_request.destination_unload, Sink | IntermediateStore):
            products_in_machine = len(transport_request.destination_pick_up.machine_storage.storage_after_process.items)
            if quantity < products_in_machine:
                quantity = products_in_machine

        return quantity

    def get_driving_speed_per_cell(self):
        return int(self.tr_list[0].driving_speed)

    def get_loading_speed(self):
        return int(self.tr_list[0].loading_speed)
