import pandas as pd

from src.monitoring.data_analysis.convert_json_data import ConvertJsonData


class CreatingWrDuringSimulationDict:
    simulation_wr_df: pd.DataFrame
    every_wr_during_simulation_data: dict[str, list[dict]]  # dict from json data: timestamp: int, entity:....
    every_wr_identification_str_list: list[str]

    def __init__(self, convert_json_data: ConvertJsonData):
        self.convert_json_data = convert_json_data
        self.simulation_wr_df = self.convert_json_data.simulation_wr_data_df

        self.every_wr_during_simulation_data = {}
        self.every_wr_identification_str_list = self.get_all_unique_wr_identification_str()

        self.get_sorted_wr_dict()

    def get_sorted_wr_dict(self):

        for identification_str in self.every_wr_identification_str_list:
            wr_list = self.get_list_wr_with_identification_numbers(identification_str)
            wr_list = self.sort_by_timestamp(wr_list)
            self.every_wr_during_simulation_data[identification_str] = wr_list

    def get_list_wr_with_identification_numbers(self, wanted_wr_identification_str: str) -> list[dict]:
        """
        This method iterates through all rows and columns of the DataFrame self.simulation_wr_df
        and compares with wanted_wr_identification_str. If equal, then it saves the cell_data in a list.
        :return list of dict's with cell_data in which identification_str == wanted_wr_identification_str
        """
        wr_list = []

        # Iteriere durch jede Zeile und jede Spalte des DataFrames self.simulation_machine_df
        for index, row in self.simulation_wr_df.iterrows():
            for col in range(self.simulation_wr_df.shape[1]):  # iteriere durch alle Spalten
                # Überprüfe, ob die Zelle None ist, bevor wir darauf zugreifen
                cell_data = row[col]
                if cell_data and isinstance(cell_data, dict):  # Wenn die Zelle ein Dictionary ist
                    # Überprüfe, ob es in der aktuellen Zelle eine 'entities'-Liste gibt
                    entities = cell_data.get('entities', [])
                    for entity in entities:
                        # Extrahiere den 'identification_number' aus den Entitäten
                        entity_data = entity.get('entity_data', {})
                        identification_str = entity_data.get('identification_str', None)
                        if identification_str == wanted_wr_identification_str:
                            wr_list.append(cell_data)

        return wr_list

    def sort_by_timestamp(self, entities_list) -> list[dict]:
        """This method sorts a list of dictionaries according to the “timestamp” in ascending order.

        :param entities_list: List of dictionaries, each containing a 'timestamp' field
        :return: The sorted list based on the 'timestamp' ascending
        """

        sorted_entities = sorted(entities_list, key=lambda x: x.get('timestamp'))

        return sorted_entities

    def get_all_unique_wr_identification_str(self) -> list[str]:
        """Creates a list with all unique 'identification_numbers' from the DataFrame self.simulation_machine_df,
        that is contained in the 'entities' list. Duplicates are automatically removed.
        :return: List with unique identification_numbers
        """
        identification_numbers = set()

        for index, row in self.simulation_wr_df.iterrows():
            for col in range(self.simulation_wr_df.shape[1]):

                cell_data = row[col]
                if cell_data and isinstance(cell_data, dict):

                    entities = cell_data.get('entities', [])
                    for entity in entities:
                        entity_data = entity.get('entity_data', {})
                        identification_number = entity_data.get('identification_str', None)
                        if identification_number:
                            identification_numbers.add(identification_number)  # Set only adds unique values

        return list(identification_numbers)
