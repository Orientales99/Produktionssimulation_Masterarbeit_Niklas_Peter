import simpy

from src.monitoring.SavingSimulationData import SavingSimulationData
from src.process_logic.machine.machine_execution import MachineExecution
from src.process_logic.machine.machine_manager import MachineManager
from src.process_logic.path_finding import PathFinding
from src.process_logic.transport_robot.tr_executing_order import TrExecutingOrder
from src.process_logic.transport_robot.tr_order_manager import TrOrderManager
from src.process_logic.working_robot_order_manager import WorkingRobotOrderManager
from src.production.production import Production
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.production.store_manager import StoreManager
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.simulation_environmnent.machine_simulation import MachineSimulation
from src.simulation_environmnent.monitoring_simulation import MonitoringSimulation
from src.simulation_environmnent.simulation_control import SimulationControl
from src.simulation_environmnent.tr_simulation import TrSimulation
from src.simulation_environmnent.visualisation_simulation import VisualisationSimulation
from src.simulation_environmnent.wr_simulation import WrSimulation


class EnvironmentSimulation:
    def __init__(self):
        self.simulation_control = SimulationControl(False, False)

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
                                          self.simulation_control)

        self.machine_execution = MachineExecution(self.env, self.manufacturing_plan, self.machine_manager,
                                                  self.store_manager, self.saving_simulation_data)
        self.machine_simulation = MachineSimulation(self.env, self.production, self.machine_manager,
                                                    self.machine_execution, self.store_manager,
                                                    self.saving_simulation_data, self.simulation_control)

        self.tr_order_manager = TrOrderManager(self.env, self.manufacturing_plan, self.machine_manager,
                                               self.store_manager)
        self.tr_executing_order = TrExecutingOrder(self.env, self.manufacturing_plan, self.path_finding,
                                                   self.machine_execution, self.machine_manager, self.store_manager,
                                                   self.saving_simulation_data)
        self.tr_simulation = TrSimulation(self.env, self.tr_order_manager, self.tr_executing_order,
                                          self.saving_simulation_data, self.simulation_control)

        # self.visualisation_simulation = VisualisationSimulation(self.env, self.production,
        #                                                         self.tr_order_manager, self.simulation_control)

        # starting processes
        #self.env.process(self.visualisation_simulation.visualize_layout())
        self.env.process(self.monitoring_simulation.start_monitoring_process())
        self.env.process(self.print_simulation_time())
        self.env.process(self.initialise_simulation_start())
        # self.env.process(self.stop_production())
        self.env.process(self.wr_simulation.start_every_wr_process())
        self.env.process(self.tr_simulation.start_every_tr_process())
        self.env.process(self.machine_simulation.run_machine_process())

    def run_simulation(self, until: int):
        self.env.run(until=until)

    def initialise_simulation_start(self):
        self.production.create_production()
        current_date = self.production.service_starting_conditions.set_starting_date_of_simulation()
        while True:
            self.manufacturing_plan.set_parameter_for_start_of_a_simulation_day(current_date)
            self.saving_simulation_data.save_daily_manufacturing_plan(current_date,
                                                                      self.manufacturing_plan.daily_manufacturing_plan)
            print("initialise_simulation_start")
            print(self.manufacturing_plan.daily_manufacturing_plan)
            yield self.env.timeout(28800)  # 8h working time
            current_date = self.manufacturing_plan.get_next_date(current_date)
            print(f"next_day: {current_date}")

    def print_simulation_time(self):
        """Printing the current simulation time in h:min:sec."""

        while True:
            sim_time = int(self.env.now)  # Simulationszeit in Sekunden
            working_days = sim_time // 28800
            hours = (sim_time % 28800) // 3600
            minutes = (sim_time % 3600) // 60
            seconds = sim_time % 60
            print(f"Simulationtime: \n"
                  f"Productionday: {working_days:02d}\n"
                  f"Time: {hours:02d}:{minutes:02d}:{seconds:02d} \n")
            yield self.env.timeout(10)

    def stop_production(self):
        yield self.env.timeout(30)
        print("stop_production True")
        self.simulation_control.stop_event = True
        yield self.env.timeout(30)
        print("stop_production False")
        self.simulation_control.stop_event = False
