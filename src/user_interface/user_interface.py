import json
import os
import subprocess
import threading
import time

import customtkinter

from src import RESOURCES, ANALYSIS_SOLUTION
from src.simulation_starter import SimulationStarter

days_dict = {"3 Tage": "3", "2 Tage": "2", "1 Tag": "1"}
algorithmus_dict = {"Kein Algorithmus": 1, "QAPFA": 2, "GA": 3, "FDP": 4}
visualization_dict = {0: "n", 1: "y"}


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Masterarbeit - Niklas Peter - 3048575")
        self.iconbitmap(RESOURCES / 'Leuphana_icon.ico')
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set the window geometry
        self.geometry(f"{screen_width}x{screen_height}")

        self.starting_conditions_frame = customtkinter.CTkFrame(master=self, fg_color="transparent")
        self.starting_conditions_frame.pack(fill="both", expand=True)

        self.progress_frame = customtkinter.CTkFrame(master=self, fg_color="transparent")

        self.finsh_frame = customtkinter.CTkFrame(master=self, fg_color="transparent")

        self.label_days = customtkinter.CTkLabel(self.starting_conditions_frame, text="Anzahl Simulationstage:",
                                                 fg_color="transparent")
        self.label_days.grid(row=1, column=0, padx=20, pady=20, sticky="W")

        self.box_day = customtkinter.CTkOptionMenu(self.starting_conditions_frame, values=list(days_dict.keys()),
                                                   button_color="#742128", fg_color="#742128",
                                                   button_hover_color="#742128")
        self.box_day.grid(row=1, column=1, padx=20, pady=20, sticky="W")

        self.label_topology_manager = customtkinter.CTkLabel(self.starting_conditions_frame,
                                                             text="Topologie Algorithmus:",
                                                             fg_color="transparent")
        self.label_topology_manager.grid(row=2, column=0, padx=20, pady=20, sticky="W")

        self.box_topology_manager = customtkinter.CTkOptionMenu(self.starting_conditions_frame,
                                                                values=list(algorithmus_dict.keys()),
                                                                button_color="#742128", fg_color="#742128",
                                                                button_hover_color="#742128")
        self.box_topology_manager.grid(row=2, column=1, padx=20, pady=20, sticky="W")

        self.label_number_of_tr = customtkinter.CTkLabel(self.starting_conditions_frame,
                                                         text="Anzahl Transport Roboter:", fg_color="transparent")
        self.label_number_of_tr.grid(row=3, column=0, padx=20, pady=20, sticky="W")

        self.box_number_of_tr = customtkinter.CTkOptionMenu(self.starting_conditions_frame,
                                                            values=["1", "2", "3", "4", "5"], button_color="#742128",
                                                            fg_color="#742128", button_hover_color="#742128")
        self.box_number_of_tr.grid(row=3, column=1, padx=20, pady=20, sticky="W")

        self.label_capacity_of_tr = customtkinter.CTkLabel(self.starting_conditions_frame,
                                                           text="Tragekapazität der Transport Roboter:",
                                                           fg_color="transparent")
        self.label_capacity_of_tr.grid(row=4, column=0, padx=20, pady=20, sticky="W")

        self.box_capacity_of_tr = customtkinter.CTkOptionMenu(self.starting_conditions_frame,
                                                              values=["100", "75", "50"], button_color="#742128",
                                                              fg_color="#742128", button_hover_color="#742128")
        self.box_capacity_of_tr.grid(row=4, column=1, padx=20, pady=20, sticky="W")

        self.label_number_of_wr = customtkinter.CTkLabel(self.starting_conditions_frame, text="Anzahl Working Roboter:",
                                                         fg_color="transparent")
        self.label_number_of_wr.grid(row=5, column=0, padx=20, pady=20, sticky="W")

        self.box_number_of_wr = customtkinter.CTkOptionMenu(self.starting_conditions_frame,
                                                            values=[ "4", "1", "2", "3", "5"], button_color="#742128",
                                                            fg_color="#742128", button_hover_color="#742128")
        self.box_number_of_wr.grid(row=5, column=1, padx=20, pady=20, sticky="W")

        self.label_number_of_test = customtkinter.CTkLabel(self.starting_conditions_frame, text="Versuchsdurchlauf")
        self.label_number_of_test.grid(row=6, column=0, padx=20, pady=20, sticky="W")

        self.box_number_of_test = customtkinter.CTkOptionMenu(self.starting_conditions_frame,
                                                              values=["1", "2", "3", "4", "5"],
                                                              button_color="#742128",
                                                              fg_color="#742128", button_hover_color="#742128")
        self.box_number_of_test.grid(row=6, column=1, padx=20, pady=20, sticky="W")

        self.label_visualization = customtkinter.CTkLabel(self.starting_conditions_frame,
                                                          text="Visualisierung der Simulation",
                                                          fg_color="transparent")
        self.label_visualization.grid(row=8, column=0, padx=20, pady=20, sticky="W")

        self.checkbox_visualization = customtkinter.CTkCheckBox(self.starting_conditions_frame, text="",
                                                                fg_color="#742128")
        self.checkbox_visualization.grid(row=8, column=1, padx=20, pady=20, sticky="W")

        self.button = customtkinter.CTkButton(self.starting_conditions_frame, text="Simulation ausführen",
                                              command=self.button_callback, fg_color="#742128")
        self.button.grid(row=100, column=0, padx=20, pady=20, sticky="W")

    def button_callback(self):

        with open(RESOURCES / "simulation_starting_conditions.json", 'r', encoding='utf-8') as psc:
            data_process_starting_conditions = json.load(psc)

        data_process_starting_conditions["Topology_manager(No algorithm (1), QAP (2), GA (3), FDP(4)"] = \
            algorithmus_dict[self.box_topology_manager.get()]
        data_process_starting_conditions["simulation_duration_in_days"] = days_dict[self.box_day.get()]
        data_process_starting_conditions["visualising_via_pygame(y/n)"] = visualization_dict[
            self.checkbox_visualization.get()]

        with open(RESOURCES / "simulation_starting_conditions.json", "w", encoding="utf-8") as f:
            json.dump(data_process_starting_conditions, f, indent=4, ensure_ascii=False)

        with open(RESOURCES / "simulation_production_working_robot_data.json", 'r', encoding='utf-8') as psc:
            data_wr_conditions = json.load(psc)
        data_wr_conditions["working_robot"][0]["number_of_robots_in_production"] = self.box_number_of_wr.get()
        with open(RESOURCES / "simulation_production_working_robot_data.json", "w", encoding="utf-8") as f:
            json.dump(data_wr_conditions, f, indent=4, ensure_ascii=False)

        with open(RESOURCES / "simulation_production_transport_robot_data.json", 'r', encoding='utf-8') as psc:
            data_tr_conditions = json.load(psc)
        data_tr_conditions["transport_robot"][0]["number_of_robots_in_production"] = self.box_number_of_tr.get()
        data_tr_conditions["transport_robot"][0]["max_loading_capacity"] = self.box_capacity_of_tr.get()
        with open(RESOURCES / "simulation_production_transport_robot_data.json", "w", encoding="utf-8") as f:
            json.dump(data_tr_conditions, f, indent=4, ensure_ascii=False)

        self.simulation_starter = SimulationStarter()

        self.simulation_thread = threading.Thread(target=self.simulation_starter.start_simulation)
        self.simulation_thread.start()
        time.sleep(1)
        self.starting_conditions_frame.destroy()

        self.label_progress_bar = customtkinter.CTkLabel(self.progress_frame, text="Ladebalken Prozesszeit")
        self.label_progress_bar.grid(row=0, column=0)

        self.progressbar = customtkinter.CTkProgressBar(self.progress_frame, orientation="horizontal",
                                                        progress_color="#742128")
        self.progressbar.grid(row=1, column=0)

        self.label_progress_bar_percent = customtkinter.CTkLabel(self.progress_frame, text=f"{0}%")
        self.label_progress_bar_percent.grid(row=2, column=0)

        self.progress_frame.pack(fill="both", expand=False)

        self.update_progress()

    def update_progress(self):
        if self.simulation_thread and self.simulation_thread.is_alive():
            progress = self.simulation_starter.environment_simulation.get_simulation_progress()
            self.progressbar.set(progress)
            self.label_progress_bar_percent.configure(text=f"{int(progress * 100)} %")
            self.after(100, self.update_progress)  # Call this function again after 1 second
        else:
            self.simulation_starter.start_analyse()
            self.simulation_starter.secure_simulation_data(int(self.box_number_of_test.get()))

            self.progress_frame.destroy()

            self.finish_simulation_text = customtkinter.CTkLabel(self.finsh_frame, text="Die Simulation wurde erfolgreich beendet.")
            self.finish_simulation_text.grid(row=0, column=0)

            folder_path = ANALYSIS_SOLUTION / 'graph_production_material'
            open_folder(folder_path)

def open_folder(folder_path):
    """
    Opens the specified folder in the file explorer.
    """
    if os.path.exists(folder_path):
        if os.name == 'nt':  # Windows
            subprocess.run(['explorer.exe', '/select,', os.path.normpath(folder_path)])
        elif os.name == 'posix':  # macOS or Linux
            subprocess.Popen(['xdg-open', folder_path])
    else:
        print(f"The folder '{folder_path}' does not exist.")
