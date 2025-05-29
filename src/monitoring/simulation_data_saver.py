import pathlib
import shutil

from src import SIMULATION_OUTPUT_DATA, ANALYSIS_SOLUTION, SIMULATION_RUNS, RESOURCES


class SimulationDataSaver:
    def __init__(self):
        pass

    def copy_folder(self, experiment_number: int):
        """
        Copies SIMULATION_OUTPUT_DATA and ANALYSIS_SOLUTION into a new folder
        called 'Experiment run {experiment_number}' within SIMULATION_RUNS.
        """
        target_base = SIMULATION_RUNS / f"Versuchsdurchlauf {experiment_number}"
        target_base.mkdir(parents=True, exist_ok=True)

        self.copy_resources_if_not_exist()

        # Beide Ordner vollständig kopieren
        self._copy_entire_folder(SIMULATION_OUTPUT_DATA, target_base)
        self._copy_entire_folder(ANALYSIS_SOLUTION, target_base)

    def copy_resources_if_not_exist(self):
        """
        Copies the RESOURCES folder to SIMULATION_RUNS if no such folder exists there.
        """
        target_path = SIMULATION_RUNS / 'resources'
        if not target_path.exists():
            shutil.copytree(RESOURCES, target_path)
            print(f"RESOURCES wurde nach {target_path} kopiert.")
        else:
            print(f"RESOURCES-Ordner existiert bereits unter {target_path}.")

    def _copy_entire_folder(self, source_folder: pathlib.Path, destination_root: pathlib.Path):
        """
        Auxiliary method for copying a folder (incl. content) to a target directory.
        """
        destination = destination_root / source_folder.name
        shutil.copytree(source_folder, destination, dirs_exist_ok=True)
