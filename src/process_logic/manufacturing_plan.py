from collections import defaultdict
from datetime import date, timedelta

import pandas as pd

from src.entity.machine.processing_order import ProcessingOrder
from src.entity.sink import Sink
from src.process_logic.good_receipt import GoodReceipt
from src.process_logic.machine.machinemanager import MachineManager
from src.production.production import Production
from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial
from src.provide_input_data.product_information_service import ProductInformationService
from src.entity.machine.machine import Machine


class ManufacturingPlan:
    production: Production
    machine_execution: MachineManager
    service_product_information: ProductInformationService
    summarised_order_list: list[Order] | None = None
    dictionary_summarised_order_per_day: dict[date, list[Order]]
    daily_manufacturing_plan: list[Order]
    process_list_for_every_machine: list[(Machine, ProcessingOrder)]
    required_materials_for_every_machine: dict = {}
    completed_orders_list: list[Order]

    def __init__(self, production, machine_execution):
        self.production = production
        self.machine_execution = machine_execution
        self.service_product_information = ProductInformationService()

        self.dictionary_summarised_order_per_day = {}
        self.daily_manufacturing_plan = []
        self.process_list_for_every_machine = []
        self.completed_orders_list = []

        self.product_order_list = self.production.service_order.generate_order_list()
        self.product_information_list = self.service_product_information.create_product_information_list()



    def set_parameter_for_start_of_a_simulation_day(self, start_date):
        self.get_daily_manufacturing_plan(start_date)
        self.set_processing_machine_list__queue_length_estimation()
        self.get_required_material_for_every_machine()
        self.get_sink_goods_issue_order_list()


    def get_daily_manufacturing_plan(self, current_date: date):
        """calling methods -> creating daily_manufacturing_plan as a list"""
        self.analyse_orders()
        self.manufacturing_sequence_per_day(current_date)
        self.sort_by_highest_product_order_count()

    def analyse_orders(self):
        """calling methods -> creating a list with summarised orders and sort them by day"""
        self.summarise_orders()
        self.sort_list_by_date()

    def summarise_orders(self):
        """Groups identical product orders on every day and calculates their total quantity.
        list summarised_order_list = Order[Product, count(how often the product was ordered), order_date, priority) """
        order_count = defaultdict(int)

        for order in self.product_order_list:
            order_for_summarise = (
                order.product.product_id,
                order.order_date,
                order.priority
            )
            order_count[order_for_summarise] += int(order.number_of_products_per_order)

        self.summarised_order_list = []
        for (product_id, order_date, priority), count in order_count.items():
            product = next(
                (product for product in self.service_product_information.product_list
                 if product.product_id == product_id), None
            )

            if product is None:
                raise ValueError(f"Produkt mit product_id {product_id} wurde nicht gefunden.")

            # Bestellungen zusammenfassen
            self.summarised_order_list.append(
                Order(
                    product,
                    count,
                    order_date,
                    priority
                )
            )

    def sort_list_by_date(self):
        """sorts the list summarised_order_list by day, the day furthest in the past is placed first on the list"""
        period_of_time = self.range_of_days()
        days = pd.date_range(period_of_time[0], period_of_time[1], freq="D").date
        self.dictionary_summarised_order_per_day = self.dictionary_summarised_order_per_day = {
            day: {"date": day, "orders": [order for order in self.summarised_order_list if order.order_date == day]}
            for day in days
        }

    def range_of_days(self) -> tuple:
        """creating a tuple (first date, last date) in the range of every order that was taken"""
        first_date = None
        last_date = None
        for order in self.summarised_order_list:
            if first_date is None or order.order_date < first_date:
                first_date = order.order_date
            if last_date is None or order.order_date > last_date:
                last_date = order.order_date
        period_of_time = (first_date, last_date)
        return period_of_time

    def manufacturing_sequence_per_day(self, current_date: date):
        """creating a list of every order for one specific date (list: daily_manufacturing_plan)"""
        orders_for_day = self.dictionary_summarised_order_per_day.get(current_date, {}).get("orders", [])
        self.daily_manufacturing_plan = orders_for_day

    def sort_by_highest_product_order_count(self):
        """sort list: daily_manufacturing_plan by the highest order (number_of_products_per_order)"""
        sorted_orders = sorted(self.daily_manufacturing_plan,
                               key=lambda order: order.number_of_products_per_order, reverse=True)

        for sequence, order in enumerate(sorted_orders):
            order.daily_manufacturing_sequence = sequence

        self.daily_manufacturing_plan = sorted_orders

    def set_processing_machine_list__queue_length_estimation(self):
        """Each machine gets a processing list. The machine with the shortest queue time gets the next order.
           Each order is added only once to avoid duplicates."""
        machine_type_list = self.production.service_entity.get_quantity_per_machine_types_list()

        for order in self.daily_manufacturing_plan:
            executing_machine_type_step_1 = order.product.processing_step_1
            for machine_type, number_of_machines_in_production in machine_type_list:
                if executing_machine_type_step_1 == machine_type:
                    identification_str_shortest_que_time = self.get_machine_str_with_shortest_queue_time(machine_type,
                                                                                                         number_of_machines_in_production)
                    for cell in self.production.entities_located[identification_str_shortest_que_time]:
                        new_cell = self.production.find_cell_in_production_layout(cell)
                        step_of_the_process = self.get_processing_step_on_machine(cell.placed_entity, order)
                        priority = max(0, order.priority.value - step_of_the_process)

                        processing_order = ProcessingOrder(order, step_of_the_process, priority)

                        if processing_order not in new_cell.placed_entity.processing_list:
                            new_cell.placed_entity.processing_list.append(processing_order)
                            self.process_list_for_every_machine.append((cell.placed_entity, processing_order))

    def get_processing_step_on_machine(self, machine: Machine, order: Order) -> int:
        """gets the processing step of the order."""
        for product in self.product_information_list:
            if order.product.identification_str == product.identification_str:
                if product.processing_step_1 == machine.machine_type:
                    return 1
                elif product.processing_step_2 == machine.machine_type:
                    return 2
                elif product.processing_step_3 == machine.machine_type:
                    return 3
                elif product.processing_step_4 == machine.machine_type:
                    return 4


    def get_machine_str_with_shortest_queue_time(self, machine_type: int,
                                                 number_of_machines_per_machine_type: int) -> str:
        """Finds the machine with the shortest queue time and returns its identification string.
           If no machine is found, an error is returned."""
        identification_str_shortest_que_time = ""
        total_shortest_que_time = float("inf")

        for identification_number in range(1, number_of_machines_per_machine_type + 1):
            identification_str = f"Ma: {machine_type}, {identification_number}"

            new_cell = self.production.find_cell_in_production_layout(
                self.production.entities_located[identification_str][1])
            machine = new_cell.placed_entity
            shortest_que_time = self.machine_execution.calculating_processing_list_queue_length(machine)

            if shortest_que_time < total_shortest_que_time:
                total_shortest_que_time = shortest_que_time
                identification_str_shortest_que_time = identification_str

        if identification_str_shortest_que_time == "":
            return Exception("Queue time couldn't be calculated. Check if every required machine type is initialised")

        return identification_str_shortest_que_time

    def get_required_material_for_every_machine(self) -> dict[str: list[ProductionMaterial, int]]:
        """Get a dictionary (key word: machine.identification_str) with the required Materials"""

        machine_type_list = self.production.service_entity.get_quantity_per_machine_types_list()
        for machine_type, number_of_machines_in_production in machine_type_list:
            for identification_number in range(1, number_of_machines_in_production + 1):
                identification_str = f"Ma: {machine_type}, {identification_number}"

                cell = self.production.find_cell_in_production_layout(
                    self.production.entities_located[identification_str][1])

                machine = cell.placed_entity
                list_with_required_material_for_one_machine = self.machine_execution.get_list_with_process_material(machine)
                if len(list_with_required_material_for_one_machine) != 0:
                    self.required_materials_for_every_machine.update({identification_str:
                                                                          list_with_required_material_for_one_machine})

        return self.required_materials_for_every_machine

    def get_list_machine_identification_str(self) -> list[str]:
        machine_type_list = self.production.service_entity.get_quantity_per_machine_types_list()
        list_machine_identification_str = []
        # get every initialised object of class Machine
        for machine_type, number_of_machines_in_production in machine_type_list:
            for identification_number in range(1, number_of_machines_in_production + 1):
                identification_str = f"Ma: {machine_type}, {identification_number}"
                list_machine_identification_str.append(identification_str)

        return list_machine_identification_str

    def get_sink_goods_issue_order_list(self):
        sink_coordinates = self.production.sink_coordinates
        sink_cell = self.production.get_cell(sink_coordinates)
        sink = sink_cell.placed_entity

        for order in self.daily_manufacturing_plan:
            sink.goods_issue_order_list.append((order, 0))

    def update_goods_issue_order_quantities(self, sink: Sink):
        """Checks the goods_issue_store for matching ProductionMaterial and updates
        the quantities in goods_issue_order_list."""

        store_items = list(sink.goods_issue_store.items)

        for i, (order, _) in enumerate(sink.goods_issue_order_list):
            matching_items = [item for item in store_items if item.production_material_id == order.product.product_id]

            sink.goods_issue_order_list[i] = (order, len(matching_items))

        self.sink_update_completed_orders(sink)

    def sink_update_completed_orders(self, sink: Sink):
        """
            Transfers completed orders from goods_issue_order_list to completed_orders_list
            if the number of available items in the store matches the order requirement.
            Also removes the corresponding items from the store.
            """
        updated_order_list = []

        for order, produced_quantity in sink.goods_issue_order_list:

            if produced_quantity >= order.number_of_products_per_order:

                self.completed_orders_list.append(order)

                items_to_remove = [
                    item for item in sink.goods_issue_store.items
                    if item.production_material_id == order.product.product_id
                ]

                for _ in range(order.number_of_products_per_order):
                    for item in items_to_remove:
                        try:
                            sink.goods_issue_store.items.remove(item)
                            items_to_remove.remove(item)
                            break
                        except ValueError:
                            pass

            else:
                updated_order_list.append((order, produced_quantity))

        sink.goods_issue_order_list = updated_order_list

    def get_next_date(self, yesterday: date) -> date:
        return yesterday + timedelta(days=1)
