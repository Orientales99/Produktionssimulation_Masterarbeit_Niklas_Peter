import random
from collections import Counter

from datetime import date

from simpy import Store

from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_robot.transport_order import TransportOrder
from src.process_logic.transport_robot.transport_request import TransportRequest
from src.entity.transport_robot.transport_robot import TransportRobot

from src.process_logic.machine.machine_manager import Machine_Manager
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.entity.machine.Process_material import ProcessMaterial
from src.process_logic.path_finding import PathFinding
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.production.store_manager import StoreManager


class TransportRobotManager_1:
    manufacturing_plan: ManufacturingPlan
    path_finding: PathFinding
    store_manager: StoreManager
    machine_execution: Machine_Manager

    material_transport_order_list = list[TransportOrder]
    tr_list = list[TransportRobot]
    entities_located_after_init = dict[str, list[Cell]]  # dict[tr.identification_str, list[Cell]
    waiting_time: int

    list_transport_request = list[TransportRequest]
    list_tr_rdy_to_get_new_order: list[TransportRobot]
    list_tr_drive_to_pick_up: list[TransportRobot]
    list_arrived_tr_on_pick_up_destination: list[TransportRobot]
    list_loaded_tr_drive_to_unload: list[TransportRobot]
    list_tr_moving_to_waiting_destination: list[TransportRobot]

    current_date: date

    def __init__(self, simulation_environment, manufacturing_plan, path_finding, machine_execution, machine_manager):
        self.env = simulation_environment
        self.manufacturing_plan = manufacturing_plan
        self.path_finding = path_finding
        self.machine_execution = machine_execution
        self.machine_manager = machine_manager

        # self.v = ProductionVisualisation(self.manufacturing_plan.production, self.env)
        self.store_manager = StoreManager(self.env)

        self.tr_list = self.manufacturing_plan.production.tr_list
        self.machine_list = self.manufacturing_plan.production.machine_list
        self.entities_located_after_init = self.manufacturing_plan.production.entities_init_located
        self.waiting_time = self.tr_list[0].working_status.waiting_time_on_path - 3

        self.list_transport_request = []

        self.list_tr_rdy_to_get_new_order = self.tr_list[:]
        self.list_tr_drive_to_pick_up = []
        self.list_arrived_tr_on_pick_up_destination = []
        self.list_loaded_tr_drive_to_unload = []
        self.list_arrived_tr_on_unload_destination = []
        self.list_tr_moving_to_waiting_destination = []

        self.material_transport_order_list = []

    def print_all_lists(self):
        print("LIST:\n")
        print("Waiting for new order:")
        for tr in self.list_tr_rdy_to_get_new_order:
            print(f"{tr.identification_str}")

        print("\nDrive to pick up:")
        for tr in self.list_tr_drive_to_pick_up:
            print(f"{tr.identification_str}")

        print("\nPick_up:")
        for tr in self.list_arrived_tr_on_pick_up_destination:
            print(f"{tr.identification_str}")

        print("\nDrive to unload:")
        for tr in self.list_loaded_tr_drive_to_unload:
            print(f"{tr.identification_str}")
        print("\n")

        print("\nUnload:")
        for tr in self.list_arrived_tr_on_unload_destination:
            print(f"{tr.identification_str}")
        print("\n")



    def get_pick_up_station(self, request_material: ProcessMaterial) -> Machine | Source | bool:
        """Determines the pickup station (Machine or Source) for the requested material"""
        if request_material.required_material.item_type.value == 0:
            source_coordinates = self.manufacturing_plan.production.source_coordinates
            source_cell = self.manufacturing_plan.production.get_cell(source_coordinates)
            return source_cell.placed_entity
        # Iterate over all machines and check their product_after_process
        for machine in self.machine_list:
            # Check if product_after_process is not None before accessing item_type
            stored_item_list = machine.machine_storage.storage_after_process.items
            for items in stored_item_list:
                if items.identification_str == request_material.required_material.identification_str:
                    return machine

        return False

    def get_transport_order_for_tr(self, tr: TransportRobot) -> bool:
        """If TR has no Transport order or has transport capacities it gets a new Transport order"""
        material_transport_order_list_local = self.material_transport_order_list[:]

        for transport_order in material_transport_order_list_local:
            if tr.transport_order is None:
                tr.transport_order = transport_order
                self.material_transport_order_list.remove(transport_order)
                if isinstance(transport_order.unload_destination, Machine):
                    transport_order.unload_destination.waiting_for_arriving_of_tr = True
                    return True
        return False

    def calculate_total_quantity_of_transport_orders(self, transport_robot) -> int:
        total_quantity_of_transport_order = 0
        for transport_order in transport_robot.transport_order:
            total_quantity_of_transport_order += transport_order.quantity
        return total_quantity_of_transport_order

    def get_path_for_tr_pick_up(self, tr: TransportRobot) -> bool:
        if tr.transport_order is not None:

            if tr.transport_order.transporting_product not in tr.material_store.items:
                path_line_list_pu = self.calculate_path_for_pick_up(tr)
                if isinstance(path_line_list_pu, list):
                    if tr in self.list_tr_rdy_to_get_new_order:
                        return True
        return False

    def calculate_path_for_pick_up(self, tr: TransportRobot):
        pick_up_destination = tr.transport_order.pick_up_station

        if isinstance(pick_up_destination, Source):
            pick_up_coordinates = self.path_finding.get_init_coordinates_from_entity(tr)
        else:
            pick_up_coordinates = self.get_coordinates_from_pick_up_destination(tr, pick_up_destination)

        path_line_list_pu = self.path_finding.get_path_for_entity(tr, pick_up_coordinates)

        if isinstance(path_line_list_pu, list):
            tr.working_status.pick_up_location_entity = pick_up_destination
            tr.working_status.driving_destination_pick_up_material = pick_up_coordinates
            tr.working_status.driving_route_pick_up_material = path_line_list_pu

        return path_line_list_pu

    def get_coordinates_from_pick_up_destination(self, transport_robot: TransportRobot,
                                                 entity: Machine | Source) -> Coordinates:
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
        if isinstance(entity, Machine):
            list_machine_cells = self.manufacturing_plan.production.entities_located.get(
                f'{entity.identification_str}', [])
            vertical_edges_of_machine = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_machine_cells)
            horizontal_edges_of_machine = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_machine_cells)

            list_transport_robot_cells = self.manufacturing_plan.production.entities_located.get(
                f'{transport_robot.identification_str}', [])
            horizontal_edges_of_tr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_transport_robot_cells)

            return Coordinates(
                horizontal_edges_of_machine[0] - (horizontal_edges_of_tr[1] - horizontal_edges_of_tr[0] + 2),
                vertical_edges_of_machine[1])

    def get_path_for_tr_unload(self, tr: TransportRobot) -> bool:
        path_line_list_ul = self.calculate_path_for_unload(tr)

        if isinstance(path_line_list_ul, list) and len(path_line_list_ul) > 0:
            return True
        else:
            return False

    def calculate_path_for_unload(self, tr: TransportRobot) -> list:
        if tr.transport_order is not None:

            unload_destination = tr.transport_order.unload_destination
            unload_coordinates = self.get_coordinates_from_unload_destination(tr, unload_destination)
            path_line_list_ul = self.path_finding.get_path_for_entity(tr, unload_coordinates)

            if isinstance(path_line_list_ul, list):
                tr.working_status.unload_location_entity = unload_destination
                tr.working_status.driving_destination_unload_material = unload_coordinates
                tr.working_status.driving_route_unload_material = path_line_list_ul
                return path_line_list_ul
            else:
                path_line_list_ul = []
                return path_line_list_ul

    def get_coordinates_from_unload_destination(self, transport_robot: TransportRobot,
                                                entity: Machine | Sink) -> Coordinates:
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

            list_transport_robot_cells = self.manufacturing_plan.production.entities_located.values(
                f'{transport_robot.identification_str}')
            vertical_edges_of_tr = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_transport_robot_cells)
            horizontal_edges_of_tr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_transport_robot_cells)

            return Coordinates(horizontal_edges_of_list[0] + (
                    self.manufacturing_plan.production.max_coordinate.x - (
                    horizontal_edges_of_tr[1] - horizontal_edges_of_tr[0] - 2)),
                               vertical_edges_of_list[1])

        # calculate path coordinates if the unload_destination is a machine:
        if isinstance(entity, Machine):
            list_machine_cells = self.manufacturing_plan.production.entities_located.get(
                f'{entity.identification_str}', [])
            vertical_edges_of_machine = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_machine_cells)
            horizontal_edges_of_machine = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_machine_cells)

            list_transport_robot_cells = self.manufacturing_plan.production.entities_located.get(
                f'{transport_robot.identification_str}', [])
            vertical_edges_of_tr = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_transport_robot_cells)
            horizontal_edges_of_tr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_transport_robot_cells)

            return Coordinates(
                horizontal_edges_of_machine[0] - (horizontal_edges_of_tr[1] - horizontal_edges_of_tr[0] + 2),
                vertical_edges_of_machine[0] + (vertical_edges_of_tr[1] - vertical_edges_of_tr[0]) - 1)

    def tr_drive_through_production_to_pick_up_destination(self, tr: TransportRobot):
        """moving the tr one step further through the production. When a tr cannot move it's waiting for waiting_time
        period until in calculates a new path. Returns a True when its on the right place."""

        if isinstance(tr.working_status.driving_route_pick_up_material, Exception):
            print(
                f'{tr.identification_str}:{self.path_finding.get_start_cell_from_entity(tr)}, '
                f'{tr.working_status.driving_route_pick_up_material}')

        if tr.working_status.waiting_for_order is False and \
                tr.working_status.driving_to_new_location is True and \
                tr.working_status.pick_up_location_entity is not None and \
                len(tr.working_status.driving_route_pick_up_material) != 0:
            start_cell = self.path_finding.get_start_cell_from_entity(tr)

            if self.path_finding.entity_movement.move_entity_one_step(
                    start_cell, tr, tr.working_status.driving_route_pick_up_material[0]) is True:
                tr.working_status.driving_route_pick_up_material.pop(0)
                tr.working_status.waiting_time_on_path = self.waiting_time
            else:
                tr.working_status.waiting_time_on_path -= 1
                if tr.working_status.waiting_time_on_path == 0:
                    path_line_list = self.path_finding.get_path_for_entity(tr,
                                                                           tr.working_status.driving_destination_pick_up_material)
                    tr.working_status.driving_route_pick_up_material = path_line_list
                    tr.working_status.waiting_time_on_path = random.randint(1, 10)

        elif len(tr.working_status.driving_route_pick_up_material) == 0:
            return True

        return False

    def pick_up_material_on_tr(self, tr: TransportRobot):
        if tr.transport_order is not None:
            # Pick Up Material from the Source
            if isinstance(tr.transport_order.pick_up_station, Source):
                if tr.transport_order.pick_up_station == tr.working_status.pick_up_location_entity:
                    items_to_load = min(
                        (tr.material_store.capacity - len(tr.material_store.items)),
                        tr.transport_order.quantity,
                        tr.transport_order.unload_destination.machine_storage.storage_before_process.capacity
                        - len(tr.transport_order.unload_destination.machine_storage.storage_before_process.items)
                    )
                    for _ in range(items_to_load):
                        tr.material_store.put(tr.transport_order.transporting_product)

            # Pick Up Material from a Machine
            elif isinstance(tr.transport_order.pick_up_station, Machine):
                if tr.transport_order.pick_up_station == tr.working_status.pick_up_location_entity:
                    items_to_load = min(
                        (tr.material_store.capacity - len(tr.material_store.items)),
                        tr.transport_order.quantity
                    )
                    if isinstance(tr.transport_order.unload_destination, Machine):
                        items_to_load = min(
                            items_to_load,
                            tr.transport_order.pick_up_station.machine_storage.storage_before_process.capacity
                            - len(tr.transport_order.pick_up_station.machine_storage.storage_before_process.items)
                        )
                    for _ in range(items_to_load):
                        tr.material_store.put(tr.transport_order.transporting_product)

                    for _ in range(items_to_load):
                        tr.transport_order.pick_up_station.machine_storage.storage_after_process.items.remove(
                            tr.transport_order.transporting_product
                        )

            # Wenn etwas aufgeladen wurde → Roboter fährt weiter
            if len(tr.material_store.items) != 0:
                tr.working_status.driving_to_new_location = True
                self.get_path_for_tr_unload(tr)
                self.list_loaded_tr_drive_to_unload.append(tr)
                return True

        return False

    def tr_drive_through_production_to_unload_destination(self, tr: TransportRobot) -> bool:
        """moving the tr one step further through the production to unload_destination.
           When a tr cannot move it's waiting for waiting_time period until in calculates a new path.
           Returns True on the right place."""

        if isinstance(tr.working_status.driving_route_unload_material, list):
            if tr.working_status.waiting_for_order is False and \
                    tr.working_status.driving_to_new_location is True and \
                    tr.working_status.unload_location_entity is not None and \
                    len(tr.working_status.driving_route_unload_material) != 0:
                start_cell = self.path_finding.get_start_cell_from_entity(tr)
                if self.path_finding.entity_movement.move_entity_one_step(start_cell, tr,
                                                                          tr.working_status.driving_route_unload_material[
                                                                              0]) is True:
                    tr.working_status.driving_route_unload_material.pop(0)
                    tr.working_status.waiting_time_on_path = self.waiting_time
                else:
                    tr.working_status.waiting_time_on_path -= 1
                    if tr.working_status.waiting_time_on_path == 0:
                        path_line_list = self.path_finding.get_path_for_entity(tr,
                                                                               tr.working_status.driving_destination_unload_material)
                        tr.working_status.driving_route_unload_material = path_line_list
                        tr.working_status.waiting_time_on_path = random.randint(1, 10)
            elif len(tr.working_status.driving_route_unload_material) == 0:
                return True

        return False

    def unload_single_tr(self, tr: TransportRobot) -> bool:

        if tr.transport_order is not None:
            if isinstance(tr.transport_order.unload_destination, Sink):
                pass
            if isinstance(tr.transport_order.unload_destination, Machine):
                if tr.working_status.unload_location_entity == tr.transport_order.unload_destination:
                    machine_store = tr.transport_order.unload_destination.machine_storage.storage_before_process
                    empty_space_machine_store = self.store_manager.count_empty_space_in_store(machine_store)
                    unload_product = tr.transport_order.transporting_product
                    loaded_product_on_tr = self.store_manager.count_number_of_one_product_type_in_store(tr.material_store, unload_product)

                    items_to_unload = min(empty_space_machine_store, loaded_product_on_tr)

                    # reduce number of required elements on machine
                    machine = tr.transport_order.unload_destination
                    for process_material in machine.process_material_list:
                        if process_material.required_material.identification_str == unload_product.identification_str:
                            process_material.quantity_required -= items_to_unload

                    # unload product
                    for _ in range(items_to_unload):
                        machine_store.put(tr.transport_order.transporting_product)
                        tr.material_store = self.store_manager.get_material_out_of_store(
                            tr.material_store, tr.transport_order.transporting_product)
                        tr.transport_order.quantity -= 1

                    tr.transport_order.unload_destination.waiting_for_arriving_of_tr = False
                    return True
        else:
            return False

    def delete_empty_tr_order(self):
        for tr in self.tr_list:
            if tr.transport_order is not None:
                if tr.transport_order.quantity == 0:
                    tr.transport_order = None

    def get_path_for_waiting_destination(self, tr: TransportRobot) -> bool:
        path_line_list_wd = self.calculate_path_for_waiting_destination(tr)
        if isinstance(path_line_list_wd, list):
            tr.working_status.driving_route_waiting_destination = path_line_list_wd
            return True

        return False

    def calculate_path_for_waiting_destination(self, tr: TransportRobot):
        waiting_destination = Source

        waiting_destination_coordinates = self.path_finding.get_init_coordinates_from_entity(tr)
        path_line_list_wd = self.path_finding.get_path_for_entity(tr, waiting_destination_coordinates)

        if isinstance(path_line_list_wd, list):
            tr.working_status.waiting_destination = waiting_destination
            tr.working_status.driving_destination_waiting_destination = waiting_destination_coordinates
            tr.working_status.driving_route_pick_up_material = path_line_list_wd

        return path_line_list_wd

    def tr_drive_through_production_to_waiting_destination(self, tr: TransportRobot) -> bool:
        """moving the tr one step further through the production. When a tr cannot move it's waiting for waiting_time
        period until in calculates a new path. Returns a True when it's on the right place."""

        if isinstance(tr.working_status.driving_route_waiting_destination, Exception):
            print(
                f'{tr.identification_str}:{self.path_finding.get_start_cell_from_entity(tr)}, '
                f'{tr.working_status.driving_route_waiting_destination}')

        if tr.working_status.waiting_for_order is True and \
                tr.working_status.driving_to_new_location is True and \
                tr.working_status.waiting_destination is not None and \
                len(tr.working_status.driving_route_waiting_destination) != 0:
            start_cell = self.path_finding.get_start_cell_from_entity(tr)

            if self.path_finding.entity_movement.move_entity_one_step(
                    start_cell, tr, tr.working_status.driving_route_waiting_destination[0]) is True:
                tr.working_status.driving_route_waiting_destination.pop(0)
                tr.working_status.waiting_time_on_path = self.waiting_time
            else:
                tr.working_status.waiting_time_on_path -= 1
                if tr.working_status.waiting_time_on_path == 0:
                    path_line_list = self.path_finding.get_path_for_entity(tr,
                                                                           tr.working_status.driving_destination_pick_up_material)
                    tr.working_status.driving_route_waiting_destination = path_line_list
                    tr.working_status.waiting_time_on_path = random.randint(1, 10)

        elif isinstance(tr.working_status.driving_route_waiting_destination, list):
            if len(tr.working_status.driving_route_waiting_destination) == 0:
                return True

        return False

    def remove_tr_from_every_list(self, tr: TransportRobot):
        """Removes TR from every list which is organising the transport process and the executing step"""

        if tr in self.list_tr_rdy_to_get_new_order:
            self.remove_all_identical_objects_of_a_list(self.list_tr_rdy_to_get_new_order, tr)

        if tr in self.list_tr_drive_to_pick_up:
            self.remove_all_identical_objects_of_a_list(self.list_tr_drive_to_pick_up, tr)

        if tr in self.list_arrived_tr_on_pick_up_destination:
            self.remove_all_identical_objects_of_a_list(self.list_arrived_tr_on_pick_up_destination, tr)

        if tr in self.list_loaded_tr_drive_to_unload:
            self.remove_all_identical_objects_of_a_list(self.list_loaded_tr_drive_to_unload, tr)

        if tr in self.list_arrived_tr_on_unload_destination:
            self.remove_all_identical_objects_of_a_list(self.list_arrived_tr_on_unload_destination, tr)

        if tr in self.list_tr_moving_to_waiting_destination:
            self.remove_all_identical_objects_of_a_list(self.list_tr_moving_to_waiting_destination, tr)

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

    def get_driving_speed_per_cell(self):
        return int(self.tr_list[0].driving_speed)

    def get_loading_speed(self):
        return int(self.tr_list[0].loading_speed)

    def remove_all_identical_objects_of_a_list(self, long_list: list, value) -> list:
        """Removes all occurrences of ‘value’ from the ‘long_list’ list..."""
        return [x for x in long_list if x != value]
