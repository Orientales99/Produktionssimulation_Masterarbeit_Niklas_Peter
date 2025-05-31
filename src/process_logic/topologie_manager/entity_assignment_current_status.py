from src.entity.intermediate_store import IntermediateStore
from src.entity.machine.machine import Machine
from src.entity.sink import Sink
from src.entity.source import Source
from src.process_logic.topologie_manager.positions_distance_matrix import PositionsDistanceMatrix
from src.production.production import Production


class EntityAssignmentCurrentStatus:
    def __init__(self, production: Production, position_distance_matrix: PositionsDistanceMatrix):
        self.production = production
        self.class_position_distance_matrix = position_distance_matrix
        self.class_position_distance_matrix.start_creating_positions_distance_matrix()
        self.positions_distance_matrix = self.class_position_distance_matrix.positions_distance_matrix

    def get_entity_assignment(self) -> list[tuple[str, str]]:
        entity_assignment = []
        for y in self.production.production_layout:
            for cell in y:
                if isinstance(cell.placed_entity, Sink):
                    entity_assignment.append((cell.cell_id, cell.placed_entity.identification_str))

                if isinstance(cell.placed_entity, Source):
                    entity_assignment.append((cell.cell_id, cell.placed_entity.identification_str))

                if isinstance(cell.placed_entity, Machine | IntermediateStore):
                    if cell.cell_id in self.positions_distance_matrix.keys():
                        entity_assignment.append((cell.cell_id, cell.placed_entity.identification_str))

        return entity_assignment
