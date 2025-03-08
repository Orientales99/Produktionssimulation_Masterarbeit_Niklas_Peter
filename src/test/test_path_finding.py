from src.data.coordinates import Coordinates
from src.data.production import Production
from src.process_logic.path_finding import PathFinding


def test_neighbors_are_found__around_source_and_sink_after_layout_init():
    # given
    pathfinding = PathFinding()
    production = Production()
    production.create_production()
    source_coordinates = production.source_coordinates
    sink_coordinates = production.sink_coordinates

    # when
    pathfinding.update_cell_neighbors_list(Coordinates(source_coordinates.x, source_coordinates.y + 1))
    above_source_neighbors_list = pathfinding.cell_neighbors_list

    pathfinding.update_cell_neighbors_list(Coordinates(source_coordinates.x, source_coordinates.y - 1))
    under_source_neighbors_list = pathfinding.cell_neighbors_list

    pathfinding.update_cell_neighbors_list(Coordinates(source_coordinates.x + 1, source_coordinates.y))
    right_source_neighbors_list = pathfinding.cell_neighbors_list

    pathfinding.update_cell_neighbors_list(Coordinates(sink_coordinates.x - 1, sink_coordinates.y))
    lef_sink_neighbors_list = pathfinding.cell_neighbors_list

    # then
    assert len(above_source_neighbors_list) == 1
    assert len(under_source_neighbors_list) == 1
    assert len(right_source_neighbors_list) == 1
    assert len(lef_sink_neighbors_list) == 1
