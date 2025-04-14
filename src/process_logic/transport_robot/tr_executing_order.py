from src.constant.constant import TransportRobotStatus
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.entity.transport_robot.transport_robot import TransportRobot
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates


class TrExecutingOrder:
    tr_list: list[TransportRobot]
    machine_list: list[Machine]
    entities_located_after_init = dict[str, list[Cell]]

    def __init__(self, simulation_environment, manufacturing_plan, path_finding, machine_execution, machine_manager):
        self.env = simulation_environment
        self.manufacturing_plan = manufacturing_plan
        self.path_finding = path_finding
        self.machine_execution = machine_execution
        self.machine_manager = machine_manager

        self.tr_list = self.manufacturing_plan.production.tr_list
        self.machine_list = self.manufacturing_plan.production.machine_list
        self.entities_located_after_init = self.manufacturing_plan.production.entities_init_located

    def start_tr_process(self):
        for tr in self.tr_list:
            self.start__moving_to_pick_up__process_for_tr(tr)

    def start__moving_to_pick_up__process_for_tr(self, tr: TransportRobot):
        destination = tr.transport_order.pick_up_station
        if self.set_driving_parameter_for_tr(tr, destination):
            # self.env.process()

    def set_driving_parameter_for_tr(self, tr: TransportRobot, destination: Machine | Sink | Source) -> bool:
        """Changes the tr.working_status parameter (Location_entity, destination_coordinates, driving_route).
         Return False: If the path cannot be determined or tr.working_status.status is wrong."""

        if tr.working_status.status == TransportRobotStatus.MOVING_TO_PICKUP:
            driving_destination_coordinates = self.get_coordinates_from_pick_up_destination(tr, destination)

        elif tr.working_status == TransportRobotStatus.MOVING_TO_DROP_OFF:
            driving_destination_coordinates = self.get_coordinates_from_unload_destination(tr, destination)

        else:
            return False

        driving_route = self.path_finding.get_path_for_entity(tr, driving_destination_coordinates)

        if isinstance(driving_route, list):
            tr.working_status.driving_destination_coordinates = driving_destination_coordinates
            tr.working_status.driving_route = driving_route
            tr.working_status.destination_location_entity = destination
            return True

        return False

    def get_coordinates_from_pick_up_destination(self, transport_robot: TransportRobot,
                                                 entity: Machine | Source) -> Coordinates:
        """Calculates the coordinates for the destination if a transport_machine wants to pick up material ether from a
        source or a machine. Input: transport_robot and the destination entity Output: Destination Coordinates"""

        # calculate path coordinates if the pick_up_destination is a source:
        if isinstance(entity, Source):
            list_entity_cells_after_init = self.entities_located_after_init.get(str(transport_robot.identification_str),
                                                                                [])

            vertical_edges_of_list = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_entity_cells_after_init)
            horizontal_edges_of_list = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_entity_cells_after_init)
            return Coordinates(horizontal_edges_of_list[0], vertical_edges_of_list[1])

        # calculate path coordinates if the pick_up_destination is a machine:
        if isinstance(entity, Machine):
            list_machine_cells = self.manufacturing_plan.production.entities_located.get(
                f'{entity.identification_str}', [])
            vertical_edges_of_machine = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_machine_cells)
            horizontal_edges_of_machine = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_machine_cells)

            list_transport_robot_cells = self.manufacturing_plan.production.entities_located.get(
                f'{transport_robot.identification_str}', [])
            horizontal_edges_of_tr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_transport_robot_cells)

            return Coordinates(
                horizontal_edges_of_machine[0] - (horizontal_edges_of_tr[1] - horizontal_edges_of_tr[0] + 2),
                vertical_edges_of_machine[1])


    def get_coordinates_from_unload_destination(self, transport_robot: TransportRobot,
                                                entity: Machine | Sink) -> Coordinates:
        """Calculates the coordinates for the destination if a transport_machine wants to drop off material ether from a
        sink or a machine. Input: transport_robot and the destination entity Output: Destination Coordinates"""

        # calculate path coordinates if the unload_destination is a sink:
        if isinstance(entity, Sink):
            list_entity_cells_after_init = self.entities_located_after_init.get(str(transport_robot.identification_str),
                                                                                [])
            vertical_edges_of_list = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_entity_cells_after_init)
            horizontal_edges_of_list = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_entity_cells_after_init)

            list_transport_robot_cells = self.manufacturing_plan.production.entities_located.values(
                f'{transport_robot.identification_str}')
            vertical_edges_of_tr = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_transport_robot_cells)
            horizontal_edges_of_tr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_transport_robot_cells)

            return Coordinates(horizontal_edges_of_list[0] + (
                    self.manufacturing_plan.production.max_coordinate.x - (
                    horizontal_edges_of_tr[1] - horizontal_edges_of_tr[0] - 2)),
                               vertical_edges_of_list[1])

        # calculate path coordinates if the unload_destination is a machine:
        if isinstance(entity, Machine):
            list_machine_cells = self.manufacturing_plan.production.entities_located.get(
                f'{entity.identification_str}', [])
            vertical_edges_of_machine = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_machine_cells)
            horizontal_edges_of_machine = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_machine_cells)

            list_transport_robot_cells = self.manufacturing_plan.production.entities_located.get(
                f'{transport_robot.identification_str}', [])
            vertical_edges_of_tr = self.manufacturing_plan.production.get_vertical_edges_of_coordinates(
                list_transport_robot_cells)
            horizontal_edges_of_tr = self.manufacturing_plan.production.get_horizontal_edges_of_coordinates(
                list_transport_robot_cells)

            return Coordinates(
                horizontal_edges_of_machine[0] - (horizontal_edges_of_tr[1] - horizontal_edges_of_tr[0] + 2),
                vertical_edges_of_machine[0] + (vertical_edges_of_tr[1] - vertical_edges_of_tr[0]) - 1)