from dataclasses import dataclass
from datetime import date

from src.entity.machine import Machine
from src.entity.transport_robot import TransportRobot
from src.order_data.production_material import ProductionMaterial
from src.process_logic.manufacturing_plan import ManufacturingPlan


@dataclass
class TransportRobotManager:
    manufacturing_plan: ManufacturingPlan
    material_transport_request_list = list[
        tuple[Machine, ProductionMaterial, int]]  # list[destination, transporting Material, quantity]
    tr_list = list[TransportRobot]

    def __init__(self, manufacturing_plan):
        self.manufacturing_plan = manufacturing_plan
        self.tr_list = self.manufacturing_plan.production.tr_list
        self.machine_list = self.manufacturing_plan.production.machine_list
        self.material_transport_request_list = []

    def get_tr_transport_request_list(self, current_date: date):
        for machine in self.machine_list:
            if len(machine.required_material_list) > 0:
                request_material = machine.required_material_list[0]
                self.material_transport_request_list.append((machine, request_material[0], request_material[1]))
        self.sort_tr_transport_request_list_by_order_priority(current_date)

        print(self.material_transport_request_list)

    def sort_tr_transport_request_list_by_order_priority(self, current_date: date):
        """Compares the transport request list with the order list and moves the transport request with the highest
        order priority to the front of the list."""

        dict_of_orders_on_current_date = self.manufacturing_plan.dictionary_summarised_order_per_day.get(current_date,
                                                                                                         [])
        list_of_orders = dict_of_orders_on_current_date['orders']

        for order in reversed(list_of_orders):
            for i, (machine, production_material, quantity) in enumerate(self.material_transport_request_list):
                product_id = production_material.identification_str.split('.')[0] + '.' + \
                             production_material.identification_str.split('.')[1]

                if product_id == order.product.product_id:
                    item = (machine, production_material, quantity)
                    self.material_transport_request_list.pop(i)
                    self.material_transport_request_list.insert(0, item)
                    break


    def get_transport_order_for_every_tr(self):
        """If TR has no Transport order or has transport capacities it gets a new Transport order """
        total_quantity_of_transport_order = 10000
        for tr in self.tr_list:
            for transport_request in self.material_transport_request_list:

                if len(tr.transport_order) != 0:
                    total_quantity_of_transport_order = self.calculate_total_quantity_of_transport_order(tr) + transport_request[2]


                if len(tr.transport_order) == 0:
                    tr.transport_order.append(transport_request)

                if total_quantity_of_transport_order <= tr.max_loading_capacity.capacity - len(tr.max_loading_capacity.items):
                    tr.transport_order.append(transport_request)

            print(f'TR:{tr.identification_str}, {tr.transport_order}')

    def calculate_total_quantity_of_transport_order(self, transport_robot) -> int:
        total_quantity_of_transport_order = 0
        for _, _, quantity in transport_robot.transport_order:
            total_quantity_of_transport_order += quantity
        return total_quantity_of_transport_order

    def get_destination_material_pick_up(self):
        pass