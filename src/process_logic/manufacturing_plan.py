import pandas as pd

from collections import defaultdict

from src.data.order import Order
from src.data.production import Production
from src.data.production_material import ProductionMaterial
from src.data.service_order import ServiceOrder
from src.data.service_product_information import ServiceProductInformation
from datetime import date


class ManufacturingPlan:
    service_order = ServiceOrder()
    service_product_information = ServiceProductInformation()
    production = Production()
    summarised_order_list: list[Order] | None
    dictionary_summarised_order_per_day: dict = {}
    daily_manufacturing_plan: list[Order] = []
    required_materials_for_every_machine: dict = {}

    def __init__(self):
        self.product_order_list = self.service_order.generate_order_list()
        self.product_information_list = self.service_product_information.create_product_information_list()

    def get_daily_manufacturing_plan(self, current_date: date):
        """calling methods -> creating daily_manufacturing_plan as a list"""
        self.analyse_orders()
        self.manufacturing_sequence_per_day(current_date)
        self.sort_by_highest_product_order_count()
        print(self.daily_manufacturing_plan)

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

        print("Keys in order_count:", list(order_count.keys()))  # Debugging-Ausgabe

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
                        if (order, 1) not in new_cell.placed_entity.processing_list:
                            new_cell.placed_entity.processing_list.append((order, 1))

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
            shortest_que_time = new_cell.placed_entity.calculating_processing_list_queue_length()

            if shortest_que_time < total_shortest_que_time:
                total_shortest_que_time = shortest_que_time
                identification_str_shortest_que_time = identification_str

        if identification_str_shortest_que_time == "":
            return Exception("Queue time couldn't be calculated. Check if every required machine type is initialised")

        return identification_str_shortest_que_time

    def get_required_material_for_every_machine(self) -> dict[str: list[ProductionMaterial, int]]:
        """Get a dictionary (key word: identification_str) with the required Materials"""

        machine_type_list = self.production.service_entity.get_quantity_per_machine_types_list()
        for machine_type, number_of_machines_in_production in machine_type_list:
            for identification_number in range(1, number_of_machines_in_production + 1):
                identification_str = f"Ma: {machine_type}, {identification_number}"

                cell = self.production.find_cell_in_production_layout(
                    self.production.entities_located[identification_str][1])

                list_with_required_material_for_one_machine = cell.placed_entity.get_list_with_required_material()
                if len(list_with_required_material_for_one_machine) != 0:
                    self.required_materials_for_every_machine.update({identification_str:
                                                                      list_with_required_material_for_one_machine})

        return self.required_materials_for_every_machine
