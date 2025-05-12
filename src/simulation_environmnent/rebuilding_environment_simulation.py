import simpy
import time

from src.monitoring.SavingSimulationData import SavingSimulationData
from src.monitoring.data_analysis.convert_json_data import ConvertJsonData
from src.monitoring.data_analysis.creating_machine_during_simulation_dict import CreatingMachineDuringSimulationDict
from src.monitoring.data_analysis.creating_sink_during_simulation_dict import CreatingSinkDuringSimulationDict
from src.monitoring.data_analysis.creating_tr_during_simulation_dict import CreatingTrDuringSimulationDict
from src.monitoring.data_analysis.creating_wr_during_simulation_dict import CreatingWrDuringSimulationDict
from src.process_logic.machine.machine_execution import MachineExecution
from src.process_logic.machine.machinemanager import MachineManager
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.process_logic.path_finding import PathFinding
from src.process_logic.transport_robot.tr_executing_order import TrExecutingOrder
from src.process_logic.transport_robot.tr_order_manager import TrOrderManager
from src.process_logic.working_robot_order_manager import WorkingRobotOrderManager
from src.production.production import Production
from src.production.store_manager import StoreManager
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.rebuild_simulation.entities_specifc_simulation_time import EntitiesSpecificSimulationTime
from src.simulation_environmnent.machine_simulation import MachineSimulation
from src.simulation_environmnent.monitoring_simulation import MonitoringSimulation
from src.simulation_environmnent.tr_simulation import TrSimulation
from src.simulation_environmnent.visualisation_simulation import VisualisationSimulation
from src.simulation_environmnent.wr_simulation import WrSimulation


class BuckFixingEnvironmentSimulation:
    def __init__(self):
        self.stop_event = False

        self.env = simpy.Environment()
        self.service_starting_conditions = StartingConditionsService()
        self.production = Production(self.env, self.service_starting_conditions)
        self.store_manager = StoreManager(self.env)
        self.path_finding = PathFinding(self.production)

        self.machine_manager = MachineManager(self.production, self.store_manager)
        self.manufacturing_plan = ManufacturingPlan(self.production, self.machine_manager)

        self.working_robot_order_manager = WorkingRobotOrderManager(self.manufacturing_plan, self.path_finding)
        self.saving_simulation_data = SavingSimulationData(self.env, self.production, self.working_robot_order_manager,
                                                           self.store_manager)
        self.monitoring_simulation = MonitoringSimulation(self.env, self.saving_simulation_data)
        self.wr_simulation = WrSimulation(self.env, self.working_robot_order_manager, self.saving_simulation_data,
                                          self.stop_event)

        self.machine_execution = MachineExecution(self.env, self.manufacturing_plan, self.machine_manager,
                                                  self.store_manager, self.saving_simulation_data)
        self.machine_simulation = MachineSimulation(self.env, self.production, self.machine_manager,
                                                    self.machine_execution, self.store_manager,
                                                    self.saving_simulation_data, self.stop_event)

        self.tr_order_manager = TrOrderManager(self.env, self.manufacturing_plan, self.machine_manager,
                                               self.store_manager)
        self.tr_executing_order = TrExecutingOrder(self.env, self.manufacturing_plan, self.path_finding,
                                                   self.machine_execution, self.machine_manager, self.store_manager,
                                                   self.saving_simulation_data)
        self.tr_simulation = TrSimulation(self.env, self.tr_order_manager, self.tr_executing_order,
                                          self.saving_simulation_data, self.stop_event)

        self.visualisation_simulation = VisualisationSimulation(self.env, self.production, self.tr_order_manager,
                                                                 self.stop_event)

        ####################################################################################################################
        self.production.create_production()
        self.control_time = self.get_control_time()

        self.convert = ConvertJsonData()
        self.creating_machine_during_simulation_dict = CreatingMachineDuringSimulationDict(self.convert)
        self.creating_tr_during_simulation_dict = CreatingTrDuringSimulationDict(self.convert)
        self.creating_wr_during_simulation_dict = CreatingWrDuringSimulationDict(self.convert)
        self.creating_sink_during_simulation_dict = CreatingSinkDuringSimulationDict(self.convert)

        self.entities_status = EntitiesSpecificSimulationTime(self.env, self.control_time, self.production,
                                                              self.creating_machine_during_simulation_dict,
                                                              self.creating_tr_during_simulation_dict,
                                                              self.creating_wr_during_simulation_dict,
                                                              self.creating_sink_during_simulation_dict)
        self.entities_status.refactor_production_layout()
        self.env.process(self.print_simulation_time())
        self.env.process(self.start_processes())

    ##################################################################################################################

    def start_processes(self):
        yield self.env.timeout(self.control_time)

        self.env.process(self.visualisation_simulation.visualize_layout())
        # self.env.process(self.wr_simulation.start_every_wr_process())
        # self.env.process(self.tr_simulation.start_every_tr_process())
        # self.env.process(self.machine_simulation.run_machine_process())

    def run_simulation(self, until: int):
        self.env.run(until=until)

    def initialise_simulation_start(self):

        current_date = self.production.service_starting_conditions.set_starting_date_of_simulation()
        while True:
            if self.env.now > self.control_time:
                self.manufacturing_plan.set_parameter_for_start_of_a_simulation_day(current_date)
                self.saving_simulation_data.save_daily_manufacturing_plan(current_date,
                                                                          self.manufacturing_plan.daily_manufacturing_plan)
                print(self.manufacturing_plan.daily_manufacturing_plan)
            yield self.env.timeout(28800)  # 8h working time
            current_date = self.manufacturing_plan.get_next_date(current_date)

    def print_simulation_time(self):
        """Printing the current simulation time in h:min:sec."""
        yield self.env.timeout(self.control_time)
        sim_time = int(self.env.now)  # Simulationszeit in Sekunden
        working_days = sim_time // 28800
        hours = (sim_time % 28800) // 3600
        minutes = (sim_time % 3600) // 60
        seconds = sim_time % 60
        print(f"Simulationtime: \n"
              f"Productionday: {working_days:02d}\n"
              f"Time: {hours:02d}:{minutes:02d}:{seconds:02d} \n")


    def get_control_time(self) -> int:
        return 36797   # return input("Bei welcher Sekunde soll die Produktion starten?")
