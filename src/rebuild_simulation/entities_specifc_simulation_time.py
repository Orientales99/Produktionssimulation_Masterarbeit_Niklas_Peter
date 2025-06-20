import simpy

from src.constant.constant import WorkingRobotStatus
from src.entity.intermediate_store import IntermediateStore
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.transport_robot.transport_robot import TransportRobot
from src.entity.working_robot.working_robot import WorkingRobot
from src.monitoring.data_analysis.creating_intermediate_store_during_simulation_dict import \
    CreatingIntermediateStoreDuringSimulationDict
from src.monitoring.data_analysis.creating_machine_during_simulation_dict import CreatingMachineDuringSimulationDict
from src.monitoring.data_analysis.creating_tr_during_simulation_dict import CreatingTrDuringSimulationDict
from src.monitoring.data_analysis.creating_wr_during_simulation_dict import CreatingWrDuringSimulationDict
from src.monitoring.data_analysis.creating_sink_during_simulation_dict import \
    CreatingSinkDuringSimulationDict
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.production.production import Production
from src.rebuild_simulation.convert_dict_to_class.convert_dict_to_intermediate_store import \
    ConvertDictToIntermediateStore
from src.rebuild_simulation.convert_dict_to_class.convert_dict_to_machine import ConvertDictToMachine
from src.rebuild_simulation.convert_dict_to_class.convert_dict_to_sink import ConvertDictToSink
from src.rebuild_simulation.convert_dict_to_class.convert_dict_to_tr import ConvertDictToTr
from src.rebuild_simulation.convert_dict_to_class.convert_dict_to_wr import ConvertDictToWr


class EntitiesSpecificSimulationTime:
    creating_machine_during_simulation_dict: CreatingMachineDuringSimulationDict
    creating_tr_during_simulation_dict: CreatingTrDuringSimulationDict
    creating_wr_during_simulation_dict: CreatingWrDuringSimulationDict

    every_machine_during_simulation_data: dict[str, list[dict]]
    every_wr_during_simulation_data: dict[str, list[dict]]
    every_tr_during_simulation_data: dict[str, list[dict]]

    entities_located: {str, list[Cell]}

    def __init__(self, env: simpy.Environment, simulation_time: int, production: Production,
                 creating_machine_during_simulation_dict: CreatingMachineDuringSimulationDict,
                 creating_tr_during_simulation_dict: CreatingTrDuringSimulationDict,
                 creating_wr_during_simulation_dict: CreatingWrDuringSimulationDict,
                 creating_sink_during_simulation_dict: CreatingSinkDuringSimulationDict,
                 creating_intermediate_store_during_simulation_dict: CreatingIntermediateStoreDuringSimulationDict
                 ):

        self.env = env
        self.simulation_time = simulation_time
        self.production = production

        self.creating_machine_during_simulation_dict = creating_machine_during_simulation_dict
        self.creating_tr_during_simulation_dict = creating_tr_during_simulation_dict
        self.creating_wr_during_simulation_dict = creating_wr_during_simulation_dict
        self.creating_sink_during_simulation_dict = creating_sink_during_simulation_dict
        self.creating_intermediate_store_during_simulation_dict = creating_intermediate_store_during_simulation_dict

        self.convert_dict_to_machine = ConvertDictToMachine(self.env)
        self.convert_dict_to_tr = ConvertDictToTr(self.env, self.production)
        self.convert_dict_to_wr = ConvertDictToWr(self.production)
        self.convert_dict_to_sink = ConvertDictToSink(self.env)
        self.convert_dict_to_intermediate_store = ConvertDictToIntermediateStore(self.env)

        self.every_machine_during_simulation_data = self.creating_machine_during_simulation_dict.every_machine_during_simulation_data
        self.every_wr_during_simulation_data = self.creating_wr_during_simulation_dict.every_wr_during_simulation_data
        self.every_tr_during_simulation_data = self.creating_tr_during_simulation_dict.every_tr_during_simulation_data
        self.every_sink_status_during_simulation_data = self.creating_sink_during_simulation_dict.simulation_sink_df
        self.every_intermediate_store_during_simulations_data = self.creating_intermediate_store_during_simulation_dict.every_intermediate_store_during_simulation_data

    def refactor_production_layout(self):
        self.entities_located = {}
        for y in self.production.production_layout:
            for cell in y:
                if isinstance(cell.placed_entity, Machine | TransportRobot | WorkingRobot | IntermediateStore):
                    cell.placed_entity = None
        self.last_know_states_machine()
        self.last_know_states_tr()
        self.last_know_states_wr()
        self.last_know_states_sink()
        self.last_know_states_intermediate_store()
        self.production.entities_located = self.entities_located

    def last_know_states_machine(self):
        """This method restores all machines to their last known state. It deserializes each machine and reads its
        top-left position from the data. Based on its size, the machine is placed into the production layout. Each
        covered Cell gets the machine as placed_entity. All cells are stored under the machine’s identification_str in
        self.entities_located"""

        machine_object_list: list[Machine] = []
        every_machine_dict = self.get_last_known_states_before_time(self.every_machine_during_simulation_data)

        for identification_str, machine_dict in every_machine_dict.items():
            cell_list: list[Cell]
            cell_list = []
            x = machine_dict["entities"][0]["x"]
            y = machine_dict["entities"][0]["y"]

            machine = self.convert_dict_to_machine.deserialize_complete_machine(machine_dict)
            machine_object_list.append(machine)

            # Put machine in Production_layout
            width = machine.size.x
            height = machine.size.y

            for dy in range(height):
                for dx in range(width):
                    cell = self.production.get_cell(Coordinates((x + dx), (y - dy)))
                    cell.placed_entity = machine
                    cell_list.append(cell)

            self.entities_located[identification_str] = cell_list

    def last_know_states_tr(self):
        """This method restores all transport robots. Each robot is deserialized and placed using its last known (x, y)
         position. Its size defines which cells it occupies. These cells get the robot as placed_entity. The cells are
         stored in self.entities_located using the robot’s identification_str."""

        tr_object_list: list[TransportRobot] = []
        every_tr_dict = self.get_last_known_states_before_time(self.every_tr_during_simulation_data)

        for identification_str, tr_dict in every_tr_dict.items():
            cell_list: list[Cell]
            cell_list = []
            x = tr_dict["entities"][0]["x"]
            y = tr_dict["entities"][0]["y"]

            tr = self.convert_dict_to_tr.deserialize_complete_transport_robot(tr_dict)
            tr_object_list.append(tr)

            width = tr.size.x
            height = tr.size.y

            for dy in range(height):
                for dx in range(width):
                    cell = self.production.get_cell(Coordinates((x + dx), (y - dy)))
                    cell.placed_entity = tr
                    cell_list.append(cell)

            self.entities_located[identification_str] = cell_list

    def last_know_states_wr(self):
        """This method restores all working robots. It reads their position and size from the data. Each robot is
        deserialized and placed into the production layout. Affected cells are updated with the robot as placed_entity.
        These cells are saved in self.entities_located under the robot’s identification_str"""

        wr_object_list: list[WorkingRobot] = []
        every_wr_dict = self.get_last_known_states_before_time(self.every_wr_during_simulation_data)

        for identification_str, wr_dict in every_wr_dict.items():
            cell_list: list[Cell]
            cell_list = []

            x = wr_dict["entities"][0]["x"]
            y = wr_dict["entities"][0]["y"]

            wr = self.convert_dict_to_wr.deserialize_complete_working_robot(wr_dict)
            wr_object_list.append(wr)

            width = wr.size.x
            height = wr.size.y

            if wr.working_status.status is not WorkingRobotStatus.WORKING_ON_MACHINE and \
                    wr.working_status.status is not WorkingRobotStatus.WAITING_IN_MACHINE_TO_EXIT:

                for dy in range(height):
                    for dx in range(width):
                        cell = self.production.get_cell(Coordinates((x + dx), (y - dy)))
                        cell.placed_entity = wr
                        cell_list.append(cell)

                self.entities_located[identification_str] = cell_list

    def last_know_states_sink(self):
        """This method restores sink. It reads their position and size from the data. Affected cells are updated with
        the sink as placed_entity.
        These cells are saved in self.entities_located under the robot’s identification_str"""

        for y in self.production.production_layout:
            for cell in y:
                if isinstance(cell.placed_entity, Sink):
                    sink_dict = self.get_last_known_states_before_time(self.every_sink_status_during_simulation_data)
                    sink = self.convert_dict_to_sink.deserialize_complete_sink(sink_dict)
                    cell.placed_entity = sink

    def last_know_states_intermediate_store(self):
        """This method restores all intermediate_stores. Each robot is deserialized and placed using its last known
           (x, y) position. Its size defines which cells it occupies. These cells get the intermediate_stores as
           placed_entity. The cells are stored in self.entities_located using the
           intermediate_stores.identification_str."""

        intermediate_stores_object_list: list[IntermediateStore] = []
        every_intermediate_stores_dict = self.get_last_known_states_before_time(
            self.every_intermediate_store_during_simulations_data)

        for identification_str, intermediate_stores_dict in every_intermediate_stores_dict.items():
            cell_list: list[Cell]
            cell_list = []
            x = intermediate_stores_dict["entities"][0]["x"]
            y = intermediate_stores_dict["entities"][0]["y"]

            intermediate_stores = self.convert_dict_to_intermediate_store.deserialize_complete_intermediate_store(
                intermediate_stores_dict)
            intermediate_stores_object_list.append(intermediate_stores)

            width = intermediate_stores.size.x
            height = intermediate_stores.size.y

            for dy in range(height):
                for dx in range(width):
                    cell = self.production.get_cell(Coordinates((x + dx), (y - dy)))
                    cell.placed_entity = intermediate_stores
                    cell_list.append(cell)

            self.entities_located[identification_str] = cell_list

    def get_last_known_states_before_time(self, entity_dict: dict[str, list[dict]]) -> dict[str, dict]:
        """
        For each entity (identified by identification_str), find the last recorded state before the given time_limit.
        :param entity_dict: Dictionary containing lists of dicts per entity with timestamped data.
        :param time_limit: The time (in seconds) up to which the state should be considered.
        :return: Dictionary with identification_str as keys and the last valid dict as values.
        """
        last_known_states = {}
        for identification_str, records in entity_dict.items():
            # Filter only those entries where timestamp <= time_limit
            valid_entries = [entry for entry in records if
                             entry is not None and entry.get("timestamp", float('inf')) <= self.simulation_time]

            if valid_entries:
                # Take the one with the highest timestamp among the valid entries
                last_entry = max(valid_entries, key=lambda x: x["timestamp"])
                last_known_states[identification_str] = last_entry
            # Optional: else, log or set default if no valid entry exists
        return last_known_states
