import pandas as pd


class CreatingMachineDuringSimulationDict:

    simulation_machine_df: pd.DataFrame
    every_machine_during_simulation_data: dict[str, list[dict]]  # dict from json data: timestamp: int, entity:....

    def __init__(self, convert_json_data):
        self.convert_json_data = convert_json_data
        self.simulation_machine_df = self.convert_json_data.simulation_machine_data_df
        self.every_machine_during_simulation_data = {}
        self.get_sorted_machine_dict()

    def get_sorted_machine_dict(self):

        identification_str_list = self.get_all_unique_identification_numbers()
        for identification_str in identification_str_list:
            machine_list = self.get_list_machine_with_identification_numbers(identification_str)
            machine_list = self.sort_by_timestamp(machine_list)
            self.every_machine_during_simulation_data[identification_str] = machine_list

    def get_all_unique_identification_numbers(self) -> list[str]:
        """Creates a list with all unique 'identification_numbers' from the DataFrame self.simulation_machine_df,
        that is contained in the 'entities' list. Duplicates are automatically removed.
        :return: List with unique identification_numbers
        """
        identification_numbers = set()

        for index, row in self.simulation_machine_df.iterrows():
            for col in range(self.simulation_machine_df.shape[1]):

                cell_data = row[col]
                if cell_data and isinstance(cell_data, dict):

                    entities = cell_data.get('entities', [])
                    for entity in entities:
                        entity_data = entity.get('entity_data', {})
                        identification_number = entity_data.get('identification_str', None)
                        if identification_number:
                            identification_numbers.add(identification_number)  # Set only adds unique values

        return list(identification_numbers)

    def get_list_machine_with_identification_numbers(self, wanted_machine_identification_str: str) -> list[dict]:
        """
        This method iterates through all rows and columns of the DataFrame self.simulation_machine_df
        and compares with wanted_machine_identification_str. If equal, then it saves the cell_data in a list.
        :return list of dict's with cell_data in which identification_str == wanted_machine_identification_str
        """
        machine_list = []

        # Iteriere durch jede Zeile und jede Spalte des DataFrames self.simulation_machine_df
        for index, row in self.simulation_machine_df.iterrows():
            for col in range(self.simulation_machine_df.shape[1]):  # iteriere durch alle Spalten
                # Überprüfe, ob die Zelle None ist, bevor wir darauf zugreifen
                cell_data = row[col]
                if cell_data and isinstance(cell_data, dict):  # Wenn die Zelle ein Dictionary ist
                    # Überprüfe, ob es in der aktuellen Zelle eine 'entities'-Liste gibt
                    entities = cell_data.get('entities', [])
                    for entity in entities:
                        # Extrahiere den 'identification_number' aus den Entitäten
                        entity_data = entity.get('entity_data', {})
                        identification_str = entity_data.get('identification_str', None)
                        if identification_str == wanted_machine_identification_str:
                            machine_list.append(cell_data)

        return machine_list

    def sort_by_timestamp(self, entities_list):
        """This method sorts a list of dictionaries according to the “timestamp” in ascending order.

        :param entities_list: List of dictionaries, each containing a 'timestamp' field
        :return: The sorted list based on the 'timestamp' ascending
        """

        sorted_entities = sorted(entities_list, key=lambda x: x.get('timestamp'))

        return sorted_entities

    def calculate_processing_time(self, machine_list: list[dict]):
        pass
