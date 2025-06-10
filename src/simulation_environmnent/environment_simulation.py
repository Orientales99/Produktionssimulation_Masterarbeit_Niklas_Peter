import simpy

from src import SIMULATION_BASIS_FOR_TOPOLOGIE_MANAGER
from src.entity.intermediate_store import IntermediateStore
from src.monitoring.SavingSimulationData import SavingSimulationData
from src.monitoring.data_analysis.convert_json_data import ConvertJsonData
from src.monitoring.data_analysis.creating_intermediate_store_during_simulation_dict import \
    CreatingIntermediateStoreDuringSimulationDict
from src.monitoring.data_analysis.creating_machine_during_simulation_dict import CreatingMachineDuringSimulationDict
from src.monitoring.data_analysis.creating_tr_during_simulation_dict import CreatingTrDuringSimulationDict
from src.monitoring.data_analysis.transport_data.material_flow import MaterialFlow
from src.monitoring.deleting_data import DeletingData
from src.process_logic.machine.machine_execution import MachineExecution
from src.process_logic.machine.machine_manager import MachineManager
from src.process_logic.path_finding import PathFinding
from src.process_logic.topologie_manager.entity_assignment_current_status import EntityAssignmentCurrentStatus
from src.process_logic.topologie_manager.forced_directed_placement import ForcedDirectedPlacement
from src.process_logic.topologie_manager.genetic_algorithm import GeneticAlgorithm
from src.process_logic.topologie_manager.positions_distance_matrix import PositionsDistanceMatrix
from src.process_logic.topologie_manager.quadratic_assignment_problem import QuadraticAssignmentProblem
from src.process_logic.topologie_manager.repositioning_objects import RepositioningObjects
from src.process_logic.transport_robot.tr_executing_order import TrExecutingOrder
from src.process_logic.transport_robot.tr_order_manager import TrOrderManager
from src.process_logic.working_robot_order_manager import WorkingRobotOrderManager
from src.production.production import Production
from src.process_logic.manufacturing_plan import ManufacturingPlan
from src.production.store_manager import StoreManager
from src.provide_input_data.order_service import OrderService
from src.provide_input_data.starting_condition_service import StartingConditionsService
from src.simulation_environmnent.machine_simulation import MachineSimulation
from src.simulation_environmnent.monitoring_simulation import MonitoringSimulation
from src.simulation_environmnent.simulation_control import SimulationControl
from src.simulation_environmnent.tr_simulation import TrSimulation
from src.simulation_environmnent.visualisation_simulation import VisualisationSimulation
from src.simulation_environmnent.wr_simulation import WrSimulation


class EnvironmentSimulation:
    class_positions_distance_matrix: PositionsDistanceMatrix
    convert_json_data: ConvertJsonData
    creating_tr_during_simulation_dict: CreatingTrDuringSimulationDict
    class_material_flow: MaterialFlow
    class_quadratic_assignment_problem: QuadraticAssignmentProblem
    repositioning_objects: RepositioningObjects

    def __init__(self, order_service: OrderService):
        self.simulation_control = SimulationControl(False, False)
        self.order_service = order_service
        self.env = simpy.Environment()
        self.service_starting_conditions = StartingConditionsService()
        self.production = Production(self.env, self.service_starting_conditions)
        self.store_manager = StoreManager(self.env)
        self.path_finding = PathFinding(self.production)

        # Manufacturing & Machine Manger Classes
        self.machine_manager = MachineManager(self.production, self.store_manager)
        self.manufacturing_plan = ManufacturingPlan(self.production, self.machine_manager, self.order_service)

        # Wr Manager & Monitoring Classes
        self.working_robot_order_manager = WorkingRobotOrderManager(self.manufacturing_plan, self.path_finding)
        self.saving_simulation_data = SavingSimulationData(self.env, self.production, self.working_robot_order_manager,
                                                           self.store_manager)
        self.monitoring_simulation = MonitoringSimulation(self.env, self.saving_simulation_data)

        self.wr_simulation = WrSimulation(self.env, self.working_robot_order_manager, self.saving_simulation_data,
                                          self.simulation_control)

        # Machine Execution Classes
        self.machine_execution = MachineExecution(self.env, self.manufacturing_plan, self.machine_manager,
                                                  self.store_manager, self.saving_simulation_data)
        self.machine_simulation = MachineSimulation(self.env, self.production, self.machine_manager,
                                                    self.machine_execution, self.store_manager,
                                                    self.saving_simulation_data, self.simulation_control)

        # Tr Manager Classes
        self.tr_order_manager = TrOrderManager(self.env, self.manufacturing_plan, self.machine_manager,
                                               self.store_manager)
        self.tr_executing_order = TrExecutingOrder(self.env, self.manufacturing_plan, self.path_finding,
                                                   self.machine_execution, self.machine_manager, self.store_manager,
                                                   self.saving_simulation_data)
        self.tr_simulation = TrSimulation(self.env, self.tr_order_manager, self.tr_executing_order,
                                          self.saving_simulation_data, self.simulation_control)

        # Deleting Class
        self.deleting_data = DeletingData()

        # Visualisation Class
        self.visualisation_simulation = VisualisationSimulation(self.env, self.production,
                                                               self.tr_order_manager, self.simulation_control)

        # starting processes
        self.env.process(self.monitoring_simulation.start_monitoring_process())
        self.env.process(self.print_simulation_time())
        self.env.process(self.initialise_simulation_start())
        self.env.process(self.wr_simulation.start_every_wr_process())
        self.env.process(self.tr_simulation.start_every_tr_process())
        self.env.process(self.machine_simulation.run_machine_process())

    def run_simulation(self):
        simulation_duration = self.production.service_starting_conditions.set_simulation_duration_per_day()
        self.env.run(until=simulation_duration)

    def initialise_simulation_start(self):
        self.production.create_production()
        current_date = self.production.service_starting_conditions.set_starting_date_of_simulation()
        self.start_simulation_visualisation_process()
        self.deleting_data.delete_every_simulation_output_data_json()

        while True:
            self.manufacturing_plan.set_parameter_for_start_of_a_simulation_day(current_date)
            self.saving_simulation_data.save_daily_manufacturing_plan(current_date,
                                                                      self.manufacturing_plan.daily_manufacturing_plan)
            self.topology_manager()
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
            yield self.env.timeout(60)

    def topology_manager(self):
        if self.env.now < 1000:
            self.convert_json_data = ConvertJsonData(SIMULATION_BASIS_FOR_TOPOLOGIE_MANAGER)
            self.class_positions_distance_matrix = PositionsDistanceMatrix(self.production)
            self.creating_tr_during_simulation_dict = CreatingTrDuringSimulationDict(self.convert_json_data)
            self.creating_intermediate_store_during_simulation_dict = CreatingIntermediateStoreDuringSimulationDict(
                self.convert_json_data)
            self.creating_machine_during_simulation_dict = CreatingMachineDuringSimulationDict(self.convert_json_data)
            self.class_material_flow = MaterialFlow(self.creating_tr_during_simulation_dict,
                                                    self.creating_machine_during_simulation_dict,
                                                    self.creating_intermediate_store_during_simulation_dict)

            self.repositioning_objects = RepositioningObjects(self.production)

        algorithm = self.production.service_starting_conditions.get_topology_manager_method()

        base = 28800
        current_time = self.env.now
        endtime = ((current_time // base) + 1) * base

        if algorithm == 1:
            # No Topology changes
            if self.env.now < 1000:
                self.entity_assignment_current_status = EntityAssignmentCurrentStatus(self.production,
                                                                                      self.class_positions_distance_matrix)
            entity_assignment = self.entity_assignment_current_status.get_entity_assignment()
            self.saving_simulation_data.save_daily_topology(entity_assignment, self.production.max_coordinate)
            print("Kein Topologie Manager wurde ausgeführt")

        elif algorithm == 2:
            # quadratic_assignment_problem
            if self.env.now < 1000:
                self.class_quadratic_assignment_problem = QuadraticAssignmentProblem(self.class_material_flow,
                                                                                     self.class_positions_distance_matrix)
            entity_assignment = self.class_quadratic_assignment_problem.start_quadratic_assignment_problem(
                start_time=self.env.now, end_time=endtime)
            self.repositioning_objects.start_repositioning_objects_in_production(entity_assignment)
            self.saving_simulation_data.save_daily_topology(entity_assignment, self.production.max_coordinate)
            print("quadratic_assignment_problem wurde ausgeführt")
            for y in self.production.production_layout:
                for cell in y:
                    if isinstance(cell.placed_entity, IntermediateStore):
                        self.saving_simulation_data.save_entity_action(cell.placed_entity)
                        break


        elif algorithm == 3:
            # Genetic algorithm
            if self.env.now < 1000:
                self.class_genetic_algorithm = GeneticAlgorithm(self.env, self.class_material_flow,
                                                                self.class_positions_distance_matrix)
            entity_assignment = self.class_genetic_algorithm.start_genetic_algorithm(start_time=self.env.now,
                                                                                     end_time=endtime)
            self.repositioning_objects.start_repositioning_objects_in_production(entity_assignment)
            self.saving_simulation_data.save_daily_topology(entity_assignment, self.production.max_coordinate)
            print("Genetic algorithm wurde ausgeführt")
            for y in self.production.production_layout:
                for cell in y:
                    if isinstance(cell.placed_entity, IntermediateStore):
                        self.saving_simulation_data.save_entity_action(cell.placed_entity)
                        break

        elif algorithm == 4:
            # Force directed placement
            if self.env.now < 1000:
                self.class_forced_directed_placement = ForcedDirectedPlacement(self.env, self.production,
                                                                               self.class_material_flow,
                                                                               self.class_positions_distance_matrix)
            entity_assignment = self.class_forced_directed_placement.start_fdp_algorithm(start_time=self.env.now,
                                                                                         end_time=endtime)
            self.repositioning_objects.start_repositioning_objects_in_production(entity_assignment)
            self.saving_simulation_data.save_daily_topology(entity_assignment, self.production.max_coordinate)
            print("Force directed placement wurde ausgeführt")
            for y in self.production.production_layout:
                for cell in y:
                    if isinstance(cell.placed_entity, IntermediateStore):
                        self.saving_simulation_data.save_entity_action(cell.placed_entity)
                        break

        time_until_next_day = endtime - self.env.now + 10

    def start_simulation_visualisation_process(self):
        if self.service_starting_conditions.set_visualising_via_matplotlib() or self.service_starting_conditions.set_visualising_via_terminal() or self.service_starting_conditions.set_visualising_via_pygames():
            self.env.process(self.visualisation_simulation.visualize_layout())


    def get_simulation_progress(self) -> float:
        progress = self.env.now / self.production.service_starting_conditions.set_simulation_duration_per_day()
        return progress
