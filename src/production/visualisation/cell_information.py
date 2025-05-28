import tkinter as tk
import threading
from collections import defaultdict
from tkinter.scrolledtext import ScrolledText
from typing import Set
from simpy import Store

from src.entity.intermediate_store import IntermediateStore
from src.entity.machine.machine import Machine
from src.entity.machine.Process_material import ProcessMaterial
from src.entity.machine.processing_order import ProcessingOrder
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_robot.transport_order import TransportOrder
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot
from src.order_data.order import Order
from src.production.base.coordinates import Coordinates
from src.production.base.cell import Cell
from src.production.production import Production


class CellInformation:
    production: Production
    current_cell_coordinates: Coordinates
    current_cell: Cell
    currently_open_windows: Set[str]

    def __init__(self, production):
        self.production = production
        self.currently_open_windows = set()

    def run_cell_information_printed(self, current_coordinates: Coordinates):
        self.current_cell_coordinates = current_coordinates
        self.get_cell()
        self.get_entity_type()

    def get_cell(self):
        self.current_cell = self.production.get_cell(self.current_cell_coordinates)

    def get_entity_type(self):
        if isinstance(self.current_cell.placed_entity, Machine):
            self.print_machine_information(self.current_cell.placed_entity)

        if isinstance(self.current_cell.placed_entity, TransportRobot):
            self.print_transport_robot_information(self.current_cell.placed_entity)

        if isinstance(self.current_cell.placed_entity, WorkingRobot):
            self.print_working_robot_information(self.current_cell.placed_entity)

        if isinstance(self.current_cell.placed_entity, Source):
            self.print_source_information()

        if isinstance(self.current_cell.placed_entity, Sink):
            self.print_sink_information(self.current_cell.placed_entity)

        if isinstance(self.current_cell.placed_entity, IntermediateStore):
            self.print_intermediate_store_information(self.current_cell.placed_entity)

        if self.current_cell.placed_entity is None:
            self.print_cell_is_none_information()

    def print_intermediate_store_information(self, intermediate_store: IntermediateStore):
        items_in_store = self.get_str_products_in_store(intermediate_store.intermediate_store)

        title = f"Cell: {intermediate_store.identification_str}"

        info_text = (
            f"Cell Coordinates:   X: {self.current_cell.cell_coordinates.x}, Y: {self.current_cell.cell_coordinates.y}\n"
            "\n"
            f"Store-ID:       {intermediate_store.identification_str}\n"
            f"\n"
            f"      Max Capacity:    {intermediate_store.intermediate_store.capacity}\n"
            f"      Contained Units: {len(intermediate_store.intermediate_store.items)}\n"
            f"      Loaded_Products: {items_in_store}\n"

        )
        self.print_information_sheet(title, info_text)

    def print_machine_information(self, machine: Machine):
        """Opens a window with information about the machine. If WR is working on this Machine a WR Information sheet
        will also be printed."""

        items_in_store_before_process = self.get_str_products_in_store(machine.machine_storage.storage_before_process)
        items_in_store_after_process = self.get_str_products_in_store(machine.machine_storage.storage_after_process)
        processing_list_str = self.get_str_processing_order_list(machine.processing_list)
        process_material_list_str = self.get_str_process_material_list(machine.process_material_list)
        produced_product = (
            machine.working_status.producing_production_material.identification_str if
            machine.working_status.producing_production_material is not None else "None")

        if machine.working_status.working_on_status:
            working_on_status = str(("processing..."))
        else:
            working_on_status = str("waiting to start process")


        title = f"Cell: {machine.identification_str}"

        info_text = (
            f"Cell Coordinates:   X: {self.current_cell.cell_coordinates.x}, Y: {self.current_cell.cell_coordinates.y}\n"
            "\n"
            f"Maschinen-ID:       {machine.identification_str}\n"
            f"\n"
            f"Machine status:     {machine.working_status.process_status.value}\n"
            f"                    {working_on_status}\n"
            f"\n"
            f"WR Status:          {machine.working_status.working_robot_status.value}\n"
            f"Waiting For TR:     {machine.working_status.waiting_for_arriving_of_tr}\n"
            f"\n"
            f"Produced Product:   {produced_product}\n"
            f"\n"
            f"Machine Qualität:   {machine.machine_quality}\n"
            f"Driving Speed:      {machine.driving_speed} field/sec.\n"
            f"Working Speed:      {machine.working_speed} sec./unit\n"
            f"Setting Up Time:    {machine.setting_up_time} sec.\n"
            f"Size:\n"
            f"   width:           {machine.size.x}\n"
            f"   height:          {machine.size.y}\n"
            "\n"
            f"Machine Storage:\n"
            f"\n"
            f"      Storage Status:       {machine.working_status.storage_status.value}"         
            f"\n"
            f"      Storage before Process:\n"
            f"           Max Capacity:    {machine.machine_storage.storage_before_process.capacity}\n"
            f"           Contained Units: {len(machine.machine_storage.storage_before_process.items)}\n"
            f"           Loaded_Products: {items_in_store_before_process}\n"
            f"\n"
            f"      Storage after Process:\n"
            f"           Max Capacity:    {machine.machine_storage.storage_after_process.capacity}\n"
            f"           Contained Units: {len(machine.machine_storage.storage_after_process.items)}\n"
            f"           Loaded_Products: {items_in_store_after_process}\n"
            f"\n"
            f"Processing List:\n{processing_list_str}\n"
            "\n"
            f"{process_material_list_str}\n"

        )

        self.print_information_sheet(title, info_text)

    def get_wr_working_on_machine(self, machine: Machine) -> WorkingRobot:
        """get a machine and figure out which wr is working on it"""
        wr_list = self.production.wr_list[:]
        for wr in wr_list:
            if wr.working_status.working_for_machine == machine:
                return wr

        raise Exception("Ein Maschine hat den status, dass ein Roboter für Sie arbeitet, während dieser es nicht tut")

    def get_str_products_in_store(self, store: Store) -> str:
        """Finds all different ProductionMaterial.identification_str and counts their frequency."""
        item_counts = defaultdict(int)
        item_count_str = ""

        for item in store.items:
            identification_str = item.identification_str
            item_counts[identification_str] += 1

        for identification, count in item_counts.items():
            item_count_str_part = str(f"Produkt-ID '{identification}' kommt {count} mal vor.\n")
            item_count_str += item_count_str_part

        if item_count_str == "":
            item_count_str = "0"

        return item_count_str

    def get_str_process_material_list(self, process_material_list: list[ProcessMaterial]) -> str:
        """Get a str with different RequiredMaterial.identification_str and counts their quantity."""
        required_material_list_str = ""

        for process_material in process_material_list:
            required_material_str = f"Required Material:   {process_material.required_material.identification_str}, Quantity: {process_material.quantity_required}\n"
            producing_material_str = f"Producing Material:  {process_material.producing_material.identification_str}, Quantity: {process_material.quantity_producing}\n"
            paragraph = f"\n"
            required_material_list_str += (required_material_str + producing_material_str + paragraph)

        if required_material_list_str == "":
            required_material_list_str = "0"

        return required_material_list_str

    def get_str_processing_order_list(self, order_list: list[ProcessingOrder]) -> str:
        order_list_str = ""

        for processing_order in order_list:
            order_int = f"           Order:                             {processing_order.order.product.identification_str}\n" \
                        f"               order_date:                    {processing_order.order.order_date}\n" \
                        f"               Number of Products:            {processing_order.order.number_of_products_per_order}\n" \
                        f"               priority:                      {processing_order.order.priority}\n" \
                        f"               step of the process:           {processing_order.step_of_the_process}\n" \
                        f"               daily_manufacturing_sequence:  {processing_order.order.daily_manufacturing_sequence} \n" \
                        f"\n"

            order_list_str += order_int

        if order_list_str == "":
            order_list_str = "0"

        return order_list_str

    def print_working_robot_information(self, working_robot: WorkingRobot):
        """Opens a window with information about the WorkingRobot."""

        title = f"Cell: {working_robot.identification_str}"
        machine_id = (working_robot.working_status.working_for_machine.identification_str
                      if working_robot.working_status.working_for_machine is not None
                      else "None")
        destination = (
            working_robot.working_status.driving_destination_coordinates if working_robot.working_status.driving_destination_coordinates is not None else "None")

        if working_robot.working_status.working_on_status:
            working_on_status = str(("processing..."))
        else:
            working_on_status = str("waiting to start process")

        if working_robot.working_status.last_placement_in_production is None:
            last_placement = None
        else:
            last_placement = [cell.cell_id for cell in working_robot.working_status.last_placement_in_production]


        info_text = (
            f"Cell Coordinates:      X: {self.current_cell.cell_coordinates.x}, Y: {self.current_cell.cell_coordinates.y}\n"
            "\n"
            f"WorkingRobot-ID:       {working_robot.identification_str}\n"
            "\n"
            f"Size:\n"
            f"   width:              {working_robot.size.x}\n"
            f"   height:             {working_robot.size.y}\n"
            "\n"
            f"Driving Speed:         {working_robot.driving_speed} field/sec.\n"
            f"Product Transfer Rate: {working_robot.product_transfer_rate} units/sec.\n"
            f"Working Status:\n"
            f"                                  {working_robot.working_status.status.value}\n"
            f"                                  {working_on_status}\n"
            f"\n"
            f"         Machine:                 {machine_id}\n"
            f"         Destination Machine:     {destination}\n"
            f"         Waiting Time On Path:    {working_robot.working_status.waiting_time_on_path} sec.\n"
            f"\n"
            f"         Driving Route:           {working_robot.working_status.driving_route}\n"
            f"\n"
            f"last_placement_in_production:     {last_placement}\n"
        )

        self.print_information_sheet(title, info_text)

    def print_transport_robot_information(self, transport_robot: TransportRobot):
        """Öffnet ein Fenster mit den Informationen zum TransportRobot."""

        transport_order_list_str = self.get_str_transport_order(transport_robot.transport_order)
        transport_material_store_str = self.get_str_products_in_store(transport_robot.material_store)
        destination = self.get_tr_driving_destination_str(
            transport_robot.working_status.destination_location_entity)
        unload_destination = self.get_tr_driving_destination_str(transport_robot.working_status.destination_location_entity)

        if transport_robot.working_status.working_on_status:
            working_on_status = str(("processing..."))
        else:
            working_on_status = str("waiting to start process")

        title = f"Cell: {transport_robot.identification_str} "

        info_text = (
            f"Cell Coordinates:        X:{self.current_cell.cell_coordinates.x}, Y:{self.current_cell.cell_coordinates.y}\n"
            "\n"
            f"TransportRobot-ID:       {transport_robot.identification_str}\n"
            "\n"
            f"Size:\n"
            f"   width:                {transport_robot.size.x}\n"
            f"   height:               {transport_robot.size.y}\n"
            "\n"
            f"Driving Speed:           {transport_robot.driving_speed} field/sec.\n"
            f"Loading Speed:           {transport_robot.loading_speed} pallet/sec.\n"
            f"\n"
            f"Transport Order:\n"
            f"{transport_order_list_str}\n"
            f"\n"
            f"Working Status:\n"
            f"              {transport_robot.working_status.status.value}\n"
            f"              {working_on_status}\n"
            f"\n"
            f"      Transport Destination:\n"
            f"              Destination                  {destination}\n"
            f"              Destination Coordinates:     {transport_robot.working_status.driving_destination_coordinates}\n"
            f"              Route:                       {transport_robot.working_status.driving_route}\n"
            "\n"
            f"Material Transport Status:\n"
            f"              Max Capacity:                {transport_robot.material_store.capacity}\n"
            f"              Contained Units:             {len(transport_robot.material_store.items)}\n"
            f"              Loaded_Products:             {transport_material_store_str}\n"

        )

        self.print_information_sheet(title, info_text)

    def get_str_transport_order(self, transport_order: TransportOrder) -> str:
        """Get a str with different RequiredMaterial.identification_str and counts their quantity."""
        transport_order_str = ""

        pick_up_station = ""
        unload_destination = ""
        if transport_order is not None:
            if isinstance(transport_order.pick_up_station, Machine | IntermediateStore):
                pick_up_station = transport_order.pick_up_station.identification_str
            elif isinstance(transport_order.pick_up_station, Source):
                pick_up_station = "Source"
            if isinstance(transport_order.unload_destination, Machine | IntermediateStore):
                unload_destination = transport_order.unload_destination.identification_str
            elif isinstance(transport_order.unload_destination, Sink):
                unload_destination = Sink

            transport_order_str = f"           Transport Order:\n" \
                                  f"                    Transporting Product: {transport_order.transporting_product.identification_str}\n" \
                                  f"                    Pick Up Destination:  {pick_up_station}\n" \
                                  f"                    Unload Destination:   {unload_destination}\n" \
                                  f"                    Quantity:             {transport_order.quantity}\n"

        if transport_order_str == "":
            transport_order_str = "0"

        return transport_order_str

    def get_tr_driving_destination_str(self, destination_entity: Machine | Sink | Source) -> str:
        """Get a str with Destination of TR."""
        destination = ""
        if isinstance(destination_entity, Machine):
            destination = f"{destination_entity.identification_str}"

        if isinstance(destination_entity, Sink):
            destination = "Sink"

        if isinstance(destination_entity, Source):
            destination = "Source"

        if destination == "":
            destination = "No Destination"

        return destination

    def print_source_information(self):
        """Opens a window with information about the Source."""
        title = "Cell: Source"
        info_text = (
            f"This Cell is The Source\n"
            f"Cell Coordinates: X:{self.current_cell.cell_coordinates.x}, Y:{self.current_cell.cell_coordinates.y}\n"
            f"\n"
            f"The Source represents the entry point in the production process, where raw materials "
            f"are introduced into the system. It serves as the origin for the incoming goods, which are picked up by "
            f"Transport robots and delivered to the machines for processing. Transport robots are responsible for "
            f"collecting products from the Source and transporting them to the relevant machines, ensuring a smooth "
            f"and continuous flow in the production system. The Source acts as the starting point where the production "
            f"process begins, supplying the necessary materials for further manufacturing.\n"
        )

        self.print_information_sheet(title, info_text)

    def print_sink_information(self, sink: Sink):
        """Opens a window with information about the machine."""
        items_in_store_before_process = self.get_str_products_in_store(sink.goods_issue_store)
        order_list_str = self.get_str_order_list(sink.goods_issue_order_list)

        info_text = (
            f"This Cell is The Sink\n"
            f"Cell Coordinates: X:{self.current_cell.cell_coordinates.x}, Y:{self.current_cell.cell_coordinates.y}\n"
            f"\n"
            f"Max Capacity:    Infinity\n"
            f"Contained Units: {len(sink.goods_issue_store.items)}\n"
            f"Products:        {items_in_store_before_process}\n"
            f"\n"
            f"good issues order list: \n"
            f" {order_list_str}\n"
            f"The Sink represents the end point in the production process, where products are removed from the system. "
            f"It serves as the destination for finished goods, marking the completion of the production flow. "
            f"Transport robots deliver completed packaged products to the Sink, ensuring the production "
            f"process maintains its flow and efficiency. The Sink acts as the warehousing or output stage, where goods "
            f"are finalized and prepared for distribution or further processing.\n"


        )

        root = tk.Tk()
        root.title("Cell: Sink")

        text_area = ScrolledText(root, wrap=tk.WORD, width=50, height=10)
        text_area.insert(tk.END, info_text)
        text_area.config(state=tk.DISABLED)
        text_area.pack(expand=True, fill="both")

        root.mainloop()

    def get_str_order_list(self, order_list: list[Order, int]) -> str:
        order_list_str = ""

        print("DEBUG: get_str_order_list wurde aufgerufen")
        print(f"DEBUG: order_list = {order_list}")

        for order, quantity_produced_items in order_list:
            print(f"DEBUG: order = {order}, type = {type(order)}")
            order_int = f"           Order:                             {order.product.identification_str}\n" \
                        f"               order_date:                    {order.order_date}\n" \
                        f"               Number of Products:            {order.number_of_products_per_order}\n" \
                        f"               Produced Products:             {quantity_produced_items}\n" \
                        f"               priority:                      {order.priority}\n" \
                        f"               daily_manufacturing_sequence:  {order.daily_manufacturing_sequence} \n\n"
            order_list_str += order_int

        if order_list_str == "":
            order_list_str = "0"

        return order_list_str

    def print_cell_is_none_information(self):
        title = "Cell: Empty"
        info_text = (
            f"This Cell is Empty\n"
            f"Cell Coordinates: X:{self.current_cell.cell_coordinates.x}, Y:{self.current_cell.cell_coordinates.y}\n"
        )

        self.print_information_sheet(title, info_text)

    @staticmethod
    def create_information_window(title: str, info_text: str, currently_open_windows: set):
        """
           Creates a new information window if it's not already open. Checks if the window with the given
           title is already in the set of open windows."""

        if title in currently_open_windows:
            return

        root = tk.Tk()
        root.title(title)

        text_area = ScrolledText(root, wrap=tk.WORD, width=50, height=10)
        text_area.insert(tk.END, info_text)
        text_area.config(state=tk.DISABLED)
        text_area.pack(expand=True, fill="both")

        def on_close():
            try:
                currently_open_windows.remove(title)
            except KeyError:
                pass

            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)
        currently_open_windows.add(title)
        root.mainloop()

    def print_information_sheet(self, title: str, info_text: str):
        """Opens an information window in a separate thread to avoid blocking the main program."""

        threading.Thread(target=CellInformation.create_information_window,
                         args=(title, info_text, self.currently_open_windows), daemon=True).start()
