import copy
import random
from collections import Counter

import simpy

from src.constant.constant import TransportRobotStatus
from src.entity.intermediate_store import IntermediateStore
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_robot.transport_robot import TransportRobot
from src.process_logic.good_receipt import GoodReceipt
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates


class TrExecutingOrder:
    tr_list: list[TransportRobot]
    machine_list: list[Machine]
    entities_located_after_init = dict[str, list[Cell]]
    goods_receipt_list: list[GoodReceipt]

    def __init__(self, simulation_environment: simpy.Environment, manufacturing_plan, path_finding, machine_execution,
                 machine_manager,
                 store_manager, saving_simulation_data):
        self.env = simulation_environment
        self.manufacturing_plan = manufacturing_plan
        self.path_finding = path_finding
        self.machine_execution = machine_execution
        self.machine_manager = machine_manager
        self.saving_simulation_data = saving_simulation_data

        self.store_manager = store_manager

        self.tr_list = self.manufacturing_plan.production.tr_list
        self.machine_list = self.manufacturing_plan.production.machine_list
        self.entities_located_after_init = self.manufacturing_plan.production.entities_init_located
        self.waiting_time = self.tr_list[0].working_status.waiting_time_on_path
        self.goods_receipt_list = []

        self.side_step_variable = 0

    def start__moving_to_pick_up__process_for_tr(self, tr: TransportRobot) -> bool:
        destination = tr.transport_order.pick_up_station
        if self.set_driving_parameter_for_tr(tr, destination):
            return True
        return False

    def start__moving_to_unload__process_for_tr(self, tr: TransportRobot) -> bool:
        destination = tr.transport_order.unload_destination
        if self.set_driving_parameter_for_tr(tr, destination):
            return True
        return False

    def start__moving_to_waiting__process_for_tr(self, tr: TransportRobot) -> bool:
        source_coordinates = self.manufacturing_plan.production.source_coordinates
        source_cell = self.manufacturing_plan.production.get_cell(source_coordinates)
        destination = source_cell.placed_entity
        if self.set_driving_parameter_for_tr(tr, destination):
            return True
        tr.working_status.status = TransportRobotStatus.IDLE
        tr.working_status.working_on_status = False
        return False

    def set_driving_parameter_for_tr(self, tr: TransportRobot,
                                     destination: Machine | Sink | Source | IntermediateStore) -> bool:
        """Changes the tr.working_status parameter (Location_entity, destination_coordinates, driving_route).
         Return False: If the path cannot be determined or tr.working_status.status is wrong."""

        if tr.working_status.status == TransportRobotStatus.MOVING_TO_PICKUP:
            driving_destination_coordinates = self.get_coordinates_from_pick_up_destination(tr, destination)

        elif tr.working_status.status == TransportRobotStatus.MOVING_TO_DROP_OFF:
            driving_destination_coordinates = self.get_coordinates_from_unload_destination(tr, destination)

        elif tr.working_status.status == TransportRobotStatus.RETURNING:
            driving_destination_coordinates = self.path_finding.get_init_coordinates_from_entity(tr)

        driving_route = self.path_finding.get_path_for_entity(tr, driving_destination_coordinates)

        if isinstance(driving_route, list):
            tr.working_status.driving_destination_coordinates = driving_destination_coordinates
            tr.working_status.driving_route = driving_route
            tr.working_status.destination_location_entity = destination
            return True

        return False

    def get_coordinates_from_pick_up_destination(self, transport_robot: TransportRobot,
                                                 entity: Machine | Source | IntermediateStore) -> Coordinates:
        """Calculates the coordinates for the destination if a transport_machine wants to pick up material ether from a
        source or a machine. Input: transport_robot and the destination entity Output: Destination Coordinates"""

        # calculate path coordinates if the pick_up_destination is a source:
        if isinstance(entity, Source):
            list_entity_cells_after_init = self.entities_located_after_init.get(str(transport_robot.identification_str),
                                                                                [])

            vertical_edges_of_list = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_entity_cells_after_init)
            horizontal_edges_of_list = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_entity_cells_after_init)
            return Coordinates(horizontal_edges_of_list[0], vertical_edges_of_list[1])

        # calculate path coordinates if the pick_up_destination is a machine:
        if isinstance(entity, Machine | IntermediateStore):
            list_entity_cells = self.manufacturing_plan.production.entities_located.get(
                f'{entity.identification_str}', [])
            vertical_edges_of_machine = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_entity_cells)
            horizontal_edges_of_machine = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_entity_cells)

            list_transport_robot_cells = self.manufacturing_plan.production.entities_located.get(
                f'{transport_robot.identification_str}', [])
            horizontal_edges_of_tr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_transport_robot_cells)

            return Coordinates(
                horizontal_edges_of_machine[0] - (horizontal_edges_of_tr[1] - horizontal_edges_of_tr[0] + 2),
                vertical_edges_of_machine[1])

    def get_coordinates_from_unload_destination(self, transport_robot: TransportRobot,
                                                entity: Machine | Sink | IntermediateStore) -> Coordinates:
        """Calculates the coordinates for the destination if a transport_machine wants to drop off material ether from a
        sink or a machine. Input: transport_robot and the destination entity Output: Destination Coordinates"""

        # calculate path coordinates if the unload_destination is a sink:
        if isinstance(entity, Sink):
            list_entity_cells_after_init = self.entities_located_after_init.get(str(transport_robot.identification_str),
                                                                                [])
            vertical_edges_of_list = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_entity_cells_after_init)
            horizontal_edges_of_list = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_entity_cells_after_init)

            list_transport_robot_cells = self.manufacturing_plan.production.entities_located.get(
                f'{transport_robot.identification_str}')
            vertical_edges_of_tr = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_transport_robot_cells)
            horizontal_edges_of_tr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_transport_robot_cells)

            return Coordinates(horizontal_edges_of_list[0] + (
                    self.manufacturing_plan.production.max_coordinate.x - (
                    horizontal_edges_of_tr[1] - horizontal_edges_of_tr[0]) - 2),
                               vertical_edges_of_list[1])

        # calculate path coordinates if the unload_destination is a machine:
        if isinstance(entity, Machine | IntermediateStore):
            list_entity_cells = self.manufacturing_plan.production.entities_located.get(
                f'{entity.identification_str}', [])
            vertical_edges_of_machine = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_entity_cells)
            horizontal_edges_of_machine = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_entity_cells)

            list_transport_robot_cells = self.manufacturing_plan.production.entities_located.get(
                f'{transport_robot.identification_str}', [])
            vertical_edges_of_tr = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_transport_robot_cells)
            horizontal_edges_of_tr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_transport_robot_cells)

            return Coordinates(
                horizontal_edges_of_machine[0] - (horizontal_edges_of_tr[1] - horizontal_edges_of_tr[0] + 2),
                vertical_edges_of_machine[0] + (vertical_edges_of_tr[1] - vertical_edges_of_tr[0]) - 1)

    def drive_tr_one_step_trough_production(self, tr: TransportRobot) -> bool | Exception:
        """moving the tr one step further through the production to destination.
           When a tr cannot move it's waiting for waiting_time period until in calculates a new path.
           Returns True on the right place."""

        start_cell_coordinates = self.path_finding.get_start_cell_from_entity(tr)
        path = tr.working_status.driving_route

        if path is None:
            path = []
            tr.working_status.driving_route = path

        if not isinstance(tr.working_status.side_step_driving_route, list):
            if isinstance(path, Exception):
                path = self.path_finding.get_path_for_entity(tr, tr.working_status.driving_destination_coordinates)
                tr.working_status.driving_route = path
                return Exception(f"drive_tr_one_step_trough_production didn't work at the time {self.env.now}. "
                                 f"{tr.identification_str}")

            if len(path) > 0:
                if self.path_finding.entity_move_service.move_entity_one_step(start_cell_coordinates, tr, path[0]) is True:
                    tr.working_status.driving_route.pop(0)
                    tr.working_status.waiting_time_on_path = self.waiting_time

                else:
                    tr.working_status.waiting_time_on_path -= 1
                    if tr.working_status.waiting_time_on_path == 0:
                        path = self.path_finding.get_path_for_entity(tr,
                                                                     tr.working_status.driving_destination_coordinates)
                        if isinstance(path, Exception):
                            self.set_side_step_driving_parameter_for_tr(tr)
                        tr.working_status.driving_route = path
                        tr.working_status.waiting_time_on_path = random.randint(1, 120)

            if isinstance(path, Exception):
                path = self.path_finding.get_path_for_entity(tr, tr.working_status.driving_destination_coordinates)
                tr.working_status.driving_route = path
                return Exception(f"drive_tr_one_step_trough_production didn't work at the time {self.env.now}. "
                                 f"{tr.identification_str}")

            if len(tr.working_status.driving_route) == 0:
                return True

            return False
        else:
            self.drive_side_step_route_one_step(tr, start_cell_coordinates)
            return False

    def drive_side_step_route_one_step(self, tr: TransportRobot, start_cell_coordinates: Coordinates):
        side_step_path = tr.working_status.side_step_driving_route
        if self.path_finding.entity_move_service.move_entity_one_step(start_cell_coordinates, tr,
                                                                      side_step_path[0]) is True:
            tr.working_status.side_step_driving_route.pop(0)

        if len(tr.working_status.side_step_driving_route) == 0:
            path = self.path_finding.get_path_for_entity(tr, tr.working_status.driving_destination_coordinates)
            tr.working_status.driving_route = path
            tr.working_status.side_step_driving_route = None

    def set_side_step_driving_parameter_for_tr(self, tr: TransportRobot):
        """Try to calculate a short path for a side step movement.
            The side step starts either at the bottom left or top right corner.
            """
        max_coordinates: Coordinates
        max_coordinates = self.manufacturing_plan.production.max_coordinate
        min_coordinates = Coordinates(4, 4)

        if self.side_step_variable % 2 == 0:
            side_step_path = self.path_finding.get_path_for_entity(tr, min_coordinates)
            if isinstance(side_step_path, Exception):
                side_step_path = self.path_finding.get_path_for_entity(tr, Coordinates(max_coordinates.x - 4,
                                                                                       max_coordinates.y - 4))
            self.side_step_variable += 1
        else:
            side_step_path = self.path_finding.get_path_for_entity(tr, Coordinates(max_coordinates.x - 2,
                                                                                       max_coordinates.y - 2))
            if isinstance(side_step_path, Exception):
                side_step_path = self.path_finding.get_path_for_entity(tr, min_coordinates)
            self.side_step_variable += 1

        if isinstance(side_step_path, Exception):
            tr.working_status.side_step_driving_route = None
            return

        # just 4 steps for the side_step
        side_step_path = side_step_path[:4]
        tr.working_status.side_step_driving_route = side_step_path

    def pick_up_material_on_tr(self, tr: TransportRobot) -> bool:
        if isinstance(tr.transport_order.pick_up_station, Source):
            self.pick_up_material_from_source(tr)
            return True

        if isinstance(tr.transport_order.pick_up_station, Machine):
            machine = tr.transport_order.pick_up_station
            self.pick_up_material_from_machine(tr, machine)
            return True

        if isinstance(tr.transport_order.pick_up_station, IntermediateStore):
            intermediate_store = tr.transport_order.pick_up_station
            self.pick_up_material_from_intermediate_store(tr, intermediate_store)
            return True

        return False

    def pick_up_material_from_source(self, tr: TransportRobot):
        pick_up_product = tr.transport_order.transporting_product
        items_to_load = min(tr.transport_order.quantity, tr.material_store.capacity)

        for _ in range(items_to_load):
            tr.material_store.put(pick_up_product)

        if items_to_load != 0:
            self.saving_simulation_data.data_goods_receipt(GoodReceipt(pick_up_product, items_to_load, self.env.now))

    def pick_up_material_from_machine(self, tr: TransportRobot, machine: Machine):
        """Add product to the TR. Quantity is the minimum from transport_order.quantity and the available product in the
        machine.machine_storage.storage_after_process. Deleting the product from the machine_storage"""

        pick_up_product = tr.transport_order.transporting_product

        available_product_in_machine_store = self.store_manager.count_number_of_one_product_type_in_store(
            machine.machine_storage.storage_after_process, pick_up_product)

        items_to_load = min(tr.transport_order.quantity, available_product_in_machine_store, tr.material_store.capacity)

        for _ in range(items_to_load):
            # adding material to TR
            tr.material_store.put(pick_up_product)
            # deleting material from machine
            machine.machine_storage.storage_after_process.items.remove(pick_up_product)

        self.machine_manager.remove_processing_order_from_machine(machine, pick_up_product)

    def pick_up_material_from_intermediate_store(self, tr: TransportRobot, intermediate_store: IntermediateStore):
        pick_up_product = tr.transport_order.transporting_product
        items_in_intermediate_store = self.store_manager.count_number_of_one_product_type_in_store(
            intermediate_store.intermediate_store, pick_up_product)

        items_to_load = min(tr.transport_order.quantity,items_in_intermediate_store, tr.material_store.capacity)

        for _ in range(items_to_load):
            tr.material_store.put(pick_up_product)
            intermediate_store.intermediate_store.items.remove(pick_up_product)

        self.saving_simulation_data.save_entity_action(intermediate_store)

    def unload_material_off_tr(self, tr: TransportRobot) -> bool:
        if isinstance(tr.transport_order.unload_destination, Sink):
            self.unload_material_to_sink(tr)
            return True

        if isinstance(tr.transport_order.unload_destination, Machine):
            self.unload_material_to_machine(tr)
            return True

        if isinstance(tr.transport_order.unload_destination, IntermediateStore):
            self.unload_material_to_intermediate_store(tr)
            return True

        return False

    def unload_material_to_sink(self, tr: TransportRobot):
        unload_product = tr.transport_order.transporting_product
        item_to_unload = self.store_manager.count_number_of_one_product_type_in_store(tr.material_store, unload_product)
        sink = tr.transport_order.unload_destination

        for _ in range(item_to_unload):
            # deleting material from TR
            tr.material_store = self.store_manager.get_material_out_of_store(tr.material_store, unload_product)
            tr.transport_order.quantity -= 1

            # adding material to machine
            sink.goods_issue_store.put(unload_product)

        self.manufacturing_plan.update_goods_issue_order_quantities(sink)
        self.saving_simulation_data.data_order_completed(unload_product, item_to_unload)
        self.saving_simulation_data.save_entity_action(sink)
        self.saving_simulation_data.save_entity_action(tr)

        store_items = self.store_manager.get_str_products_in_store(sink.goods_issue_store)

    def unload_material_to_machine(self, tr: TransportRobot):

        unload_product = tr.transport_order.transporting_product
        item_to_unload = self.store_manager.count_number_of_one_product_type_in_store(tr.material_store, unload_product)
        machine = tr.transport_order.unload_destination

        # reduce number of required elements on machine
        for process_material in machine.process_material_list:
            if process_material.required_material.identification_str == unload_product.identification_str:
                process_material.quantity_required -= item_to_unload

        for _ in range(item_to_unload):
            # adding material to machine
            machine.machine_storage.storage_before_process.put(unload_product)

            # deleting material from TR
            tr.material_store = self.store_manager.get_material_out_of_store(tr.material_store, unload_product)
            tr.transport_order.quantity -= 1

    def unload_material_to_intermediate_store(self, tr: TransportRobot):
        unload_product = tr.transport_order.transporting_product
        item_to_unload = self.store_manager.count_number_of_one_product_type_in_store(tr.material_store, unload_product)
        intermediate_store = tr.transport_order.unload_destination
        for _ in range(item_to_unload):
            # adding material to intermediate_store
            intermediate_store.intermediate_store.put(unload_product)

            # deleting material from TR
            tr.material_store = self.store_manager.get_material_out_of_store(tr.material_store, unload_product)
            tr.transport_order.quantity -= 1

        self.saving_simulation_data.save_entity_action(intermediate_store)

    def check_if_tr_is_on_waiting_place(self, tr: TransportRobot) -> bool:
        """ Checks if the TR is in the right waiting position. The waiting position is the place where the
        TR was initiated."""

        coords_1 = [(cell.cell_coordinates.x, cell.cell_coordinates.y) for cell in
                    self.entities_located_after_init[tr.identification_str]]
        coords_2 = [(cell.cell_coordinates.x, cell.cell_coordinates.y) for cell in
                    self.manufacturing_plan.production.entities_located[tr.identification_str]]

        if Counter(coords_1) == Counter(coords_2):
            return True
        else:
            return False
