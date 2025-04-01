from datetime import date

from src.entity.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_order import TransportOrder
from src.entity.transport_robot import TransportRobot
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.entity.required_material import RequiredMaterial
from src.process_logic.path_finding import PathFinding
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.production.production_visualisation import ProductionVisualisation
from src.production.store_manager import StoreManager



class TransportRobotManager:
    manufacturing_plan: ManufacturingPlan
    path_finding: PathFinding
    store_manager: StoreManager
    material_transport_request_list = list[TransportOrder]
    tr_list = list[TransportRobot]
    entities_located_after_init = dict[str, list[Cell]]  # dict[tr.identification_str, list[Cell]
    waiting_time: int
    list_tr_rdy_to_calculate_path: list[TransportRobot]
    list_tr_drive_to_pick_up: list[TransportRobot]
    list_arrived_tr_on_pick_up_destination: list[TransportRobot]
    list_loaded_tr_drive_to_unload: list[TransportRobot]

    current_date: date

    def __init__(self, simulation_environment, manufacturing_plan, path_finding):
        self.env = simulation_environment
        self.manufacturing_plan = manufacturing_plan
        self.path_finding = path_finding

        self.v = ProductionVisualisation(self.manufacturing_plan.production)
        self.store_manager = StoreManager(self.env)

        self.tr_list = self.manufacturing_plan.production.tr_list
        self.machine_list = self.manufacturing_plan.production.machine_list
        self.entities_located_after_init = self.manufacturing_plan.production.entities_init_located
        self.waiting_time = self.tr_list[0].working_status.waiting_time_on_path - 3

        self.list_tr_rdy_to_calculate_path = self.tr_list[:]
        self.list_tr_drive_to_pick_up = []
        self.list_arrived_tr_on_pick_up_destination = []
        self.list_loaded_tr_drive_to_unload = []
        self.arrived_tr_on_unload_destination = []

        self.material_transport_request_list = []

    def start_transport_robot_manager(self, current_date):
        self.current_date = current_date
        self.get_tr_transport_request_list(current_date)
        for tr in self.tr_list:
            self.get_transport_order_for_tr(tr)
            self.get_path_for_tr(tr)

    def path_calculation_for_every_requesting_tr(self):
        if len(self.list_tr_rdy_to_calculate_path) != 0:
            for tr in self.list_tr_rdy_to_calculate_path[:]:
                self.get_path_for_tr(tr)
        pass

    def get_tr_transport_request_list(self, current_date: date):
        """Generates a list of transport requests for transport robots (TR) based on the material requirements of
        machines for one day."""
        self.material_transport_request_list = []
        for machine in self.machine_list:
            if len(machine.required_material_list) > 0:
                request_material = machine.required_material_list[0]
                pick_up_station = self.get_pick_up_station(request_material)
                self.material_transport_request_list.append(
                    TransportOrder(machine, pick_up_station, request_material.required_material,
                                   request_material.quantity))
        self.sort_tr_transport_request_list_by_order_priority(current_date)

    def get_pick_up_station(self, request_material: RequiredMaterial) -> Machine | Source:
        """Determines the pickup station (Machine or Source) for the requested material"""
        if request_material.required_material.item_type == 0:
            source_coordinates = self.manufacturing_plan.production.source_coordinates
            source_cell = self.manufacturing_plan.production.get_cell(source_coordinates)
            return source_cell.placed_entity

        for machine in self.machine_list:
            stored_item = machine.machine_storage.product_after_process.item_type
            if stored_item == request_material.required_material:
                return machine

        raise Exception(f"Required Material{request_material.required_material} is nowhere in the Production")

    def sort_tr_transport_request_list_by_order_priority(self, current_date: date):
        """Compares the transport request list with the order list and moves the transport request with the highest
        order priority to the front of the list."""

        dict_of_orders_on_current_date = self.manufacturing_plan.dictionary_summarised_order_per_day.get(current_date,
                                                                                                         [])
        list_of_orders = dict_of_orders_on_current_date['orders']

        for order in reversed(list_of_orders):
            for i, transport_order in enumerate(self.material_transport_request_list):
                product_id = transport_order.transporting_product.identification_str.split('.')[0] + '.' + \
                             transport_order.transporting_product.identification_str.split('.')[1]

                if product_id == order.product.product_id:
                    item = transport_order
                    self.material_transport_request_list.remove(i)
                    self.material_transport_request_list.insert(0, item)
                    break

    def get_transport_order_for_tr(self, tr: TransportRobot):
        """If TR has no Transport order or has transport capacities it gets a new Transport order"""
        total_quantity_of_transport_order = 10000

        material_transport_request_list_local = self.material_transport_request_list[:]

        for transport_request in material_transport_request_list_local:
            if len(tr.transport_order_list) == 0:
                tr.transport_order_list.append(transport_request)
                self.material_transport_request_list.remove(transport_request)
                tr.working_status.waiting_for_order = False

        if self.material_transport_request_list:  # is list not empty
            for tr in self.tr_list:
                material_transport_request_list_local = self.material_transport_request_list[:]

                for transport_request in material_transport_request_list_local:

                    if len(tr.transport_order_list) != 0:
                        total_quantity_of_transport_order = self.calculate_total_quantity_of_transport_orders(tr) + \
                                                            transport_request.quantity
                    if total_quantity_of_transport_order <= tr.material_store.capacity - len(
                            tr.material_store.items):
                        tr.transport_order_list.append(transport_request)
                        tr.working_status.waiting_for_order = False
                        self.material_transport_request_list.remove(transport_request)

    def calculate_total_quantity_of_transport_orders(self, transport_robot) -> int:
        total_quantity_of_transport_order = 0
        for transport_order in transport_robot.transport_order_list:
            total_quantity_of_transport_order += transport_order.quantity
        return total_quantity_of_transport_order

    def get_path_for_tr(self, tr: TransportRobot):
        """Is calculating the path for the TR. It is looking on the tr.transport_order_list and gets the path line
        to the pick_up_station and unload_station"""

        for index, transport_order in enumerate(tr.transport_order_list):
            # calculate_path_for_pick_up
            pick_up_destination = tr.transport_order_list[index].pick_up_station

            if isinstance(pick_up_destination, Source):
                pick_up_coordinates = self.path_finding.get_init_coordinates_from_entity(tr)
            else:
                pick_up_coordinates = self.get_coordinates_from_pick_up_destination(tr, pick_up_destination)
            path_line_list_pu = self.path_finding.get_path_for_entity(tr, pick_up_coordinates)

            if index == 0 and isinstance(path_line_list_pu, list):
                tr.working_status.pick_up_location_entity = pick_up_destination
                tr.working_status.driving_destination_pick_up_material = pick_up_coordinates
                tr.working_status.driving_route_pick_up_material = path_line_list_pu
            print(f'{index}, {tr.identification_str}: {path_line_list_pu}')
            print(f'Pick_Up Destination: {pick_up_destination.identification_str}')
            print()

            # calculate_path_for_unload
            unload_destination = tr.transport_order_list[index].unload_destination
            unload_coordinates = self.get_coordinates_from_unload_destination(tr, unload_destination)
            path_line_list_ul = self.path_finding.get_path_for_entity(tr, unload_coordinates)

            if index == 0 and isinstance(path_line_list_ul, list):
                tr.working_status.unload_location_entity = unload_destination
                tr.working_status.driving_destination_unload_material = unload_coordinates
                tr.working_status.driving_route_unload_material = path_line_list_ul
            print(f'Unload:{index}, {tr.identification_str}: {path_line_list_ul} ')
            print(f'Unload Destination: {unload_destination.identification_str}')
            print()
            if isinstance(path_line_list_ul, list) and isinstance(path_line_list_pu, list):
                if tr in self.list_tr_rdy_to_calculate_path:
                    self.list_tr_rdy_to_calculate_path.remove(tr)

                    self.list_tr_drive_to_pick_up.append(tr)

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

            list_transport_robot_cells = self.manufacturing_plan.production.entities_located.values(
                f'{transport_robot.identification_str}')
            horizontal_edges_of_tr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_transport_robot_cells)

            return Coordinates(
                horizontal_edges_of_machine[0] - (horizontal_edges_of_tr[1] - horizontal_edges_of_tr[0] + 2),
                vertical_edges_of_machine[1])

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

    def tr_drive_through_production_to_pick_up_destination(self):
        """moving the tr one step further through the production. When a tr cannot move it's waiting for waiting_time
        period until in calculates a new path. Return a list of TransportRobots who are on the right place."""

        list_tr_drive_to_pick_up_local = self.list_tr_drive_to_pick_up[:]

        for tr in list_tr_drive_to_pick_up_local:
            if isinstance(tr.working_status.driving_route_pick_up_material, Exception):
                self.v.visualize_layout()
                print(
                    f'{tr.identification_str}:{self.path_finding.get_start_cell_from_entity(tr)}, {tr.working_status.driving_route_pick_up_material}')

            if tr.working_status.waiting_for_order is False and tr.working_status.pick_up_location_entity is not None \
                    and len(tr.working_status.driving_route_pick_up_material) != 0:

                start_cell = self.path_finding.get_start_cell_from_entity(tr)

                if self.path_finding.entity_movement.move_entity_one_step(start_cell, tr,
                                                                          tr.working_status.driving_route_pick_up_material[
                                                                              0]) is True:
                    tr.working_status.driving_route_pick_up_material.pop(0)
                    tr.working_status.waiting_time_on_path = self.waiting_time

                else:
                    tr.working_status.waiting_time_on_path -= 1
                    if tr.working_status.waiting_time_on_path == 0:
                        path_line_list = self.path_finding.get_path_for_entity(tr,
                                                                               tr.working_status.driving_destination_pick_up_material)
                        tr.working_status.driving_route_pick_up_material = path_line_list

            elif len(tr.working_status.driving_route_pick_up_material) == 0:
                self.list_arrived_tr_on_pick_up_destination.append(tr)
                # print(f'Arrived_tr_on_pick_up: {self.list_arrived_tr_on_pick_up_destination}')
                self.list_tr_drive_to_pick_up.remove(tr)
                # print(f'Drive_to_pick_up: {self.list_tr_drive_to_pick_up}')

    def pick_up_material_on_tr(self):
        list_arrived_tr_on_pick_up_destination_local = self.list_arrived_tr_on_pick_up_destination[:]

        for tr in list_arrived_tr_on_pick_up_destination_local:

            for transport_order in tr.transport_order_list:

                # Pick Up Material from the Source
                if isinstance(transport_order.pick_up_station, Source):
                    if transport_order.pick_up_station == tr.working_status.pick_up_location_entity:
                        items_to_load = min((tr.material_store.capacity - len(tr.material_store.items)),
                                            transport_order.quantity,
                                            transport_order.unload_destination.machine_storage.storage_before_process.capacity
                                            - len(
                                                transport_order.unload_destination.machine_storage.storage_before_process.items))

                        for _ in range(items_to_load):
                            tr.material_store.put(transport_order.transporting_product)

                # Pick Up Material from a Machine
                if isinstance(transport_order.pick_up_station, Machine):
                    if transport_order.pick_up_station == tr.working_status.pick_up_location_entity:

                        items_to_load = min((tr.material_store.capacity - len(tr.material_store.items)),
                                            transport_order.quantity)

                        if isinstance(transport_order.unload_destination, Machine):
                            items_to_load = min(items_to_load,
                                                transport_order.pick_up_station.machine_storage.storage_before_process.capacity
                                                - len(
                                                    transport_order.pick_up_station.machine_storage.storage_before_process.items))

                        for _ in range(items_to_load):
                            tr.material_store.put(transport_order.transporting_product)

                        for _ in range(items_to_load):
                            tr.material_store.get(
                                transport_order.pick_up_station.machine_storage.storage_after_process)

            if len(tr.material_store.items) != 0:
                self.list_arrived_tr_on_pick_up_destination.remove(tr)
                self.list_loaded_tr_drive_to_unload.append(tr)

    def tr_drive_through_production_to_unload_destination(self):
        """moving the tr one step further through the production to unload_destination.
           When a tr cannot move it's waiting for waiting_time period until in calculates a new path.
           Return a list of TransportRobots who are on the right place."""

        list_loaded_tr_drive_to_unload_local = self.list_loaded_tr_drive_to_unload[:]

        for tr in list_loaded_tr_drive_to_unload_local:
            if isinstance(tr.working_status.driving_route_unload_material, Exception):
                self.v.visualize_layout()

            if tr.working_status.waiting_for_order is False and tr.working_status.unload_location_entity is not None \
                    and len(tr.working_status.driving_route_unload_material) != 0:

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

            elif len(tr.working_status.driving_route_unload_material) == 0:
                self.arrived_tr_on_unload_destination.append(tr)
                self.list_loaded_tr_drive_to_unload.remove(tr)

    def unload_material_from_tr(self):
        arrived_tr_on_unload_destination_local = self.arrived_tr_on_unload_destination[:]

        for tr in arrived_tr_on_unload_destination_local:
            transport_order_list_local = tr.transport_order_list
            for transport_order in transport_order_list_local:

                # Unload material in Sink
                if isinstance(transport_order.unload_destination, Sink):
                    pass

                # Unload Material on a Machine
                if isinstance(transport_order.unload_destination, Machine):
                    if tr.working_status.unload_location_entity == transport_order.unload_destination:
                        machine_store = transport_order.unload_destination.machine_storage.storage_before_process
                        empty_space_machine_store = self.store_manager.count_empty_space_in_store(machine_store)

                        tr_store = tr.material_store
                        unload_product = transport_order.transporting_product
                        loaded_product_on_tr = self.store_manager.count_products_in_store(tr_store, unload_product)

                        items_to_unload = min(empty_space_machine_store, loaded_product_on_tr)

                        for _ in range(items_to_unload):
                            machine_store.put(transport_order.transporting_product)
                            tr.material_store = self.store_manager.get_material_out_of_store(tr.material_store,
                                                                                             transport_order.transporting_product)
                            # tr.material_store.get(transport_order.transporting_product)
                            transport_order.quantity -= 1

                    if transport_order.quantity == 0:
                        tr.transport_order_list.remove(transport_order)
                        transport_order.unload_destination.get_list_with_required_material()

                        tr.working_status.driving_to_new_location = False
                        tr.working_status.waiting_for_order = True

                        self.get_transport_order_for_tr(tr)

            self.arrived_tr_on_unload_destination.remove(tr)
            self.list_tr_rdy_to_calculate_path.append(tr)

            pass

    def get_driving_speed_per_cell(self):
        return int(self.tr_list[0].driving_speed)
