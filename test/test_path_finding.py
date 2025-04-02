from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.production.production import Production
from src.production.visualisation.production_visualisation import ProductionVisualisation
from src.entity.working_robot import WorkingRobot
from src.process_logic.path_finding import PathFinding


def test_neighbors_are_found__around_source_and_sink_after_layout_init():
    # given
    production = Production()
    pathfinding = PathFinding(production)
    production.max_coordinate = Coordinates(15, 15)
    production.build_layout()
    production.set_source_in_production_layout()
    production.set_sink_in_production_layout()
    source_coordinates = production.source_coordinates
    sink_coordinates = production.sink_coordinates
    current_cell_above_source = production.get_cell(Coordinates(source_coordinates.x, source_coordinates.y + 1))
    current_cell_under_source = production.get_cell(Coordinates(source_coordinates.x, source_coordinates.y - 1))
    current_cell_right_source = production.get_cell(Coordinates(source_coordinates.x + 1, source_coordinates.y))
    current_cell_left_sink = production.get_cell(Coordinates(sink_coordinates.x - 1, sink_coordinates.y))
    # when

    above_source_neighbors_list = pathfinding.get_current_cell_neighbors(
        Coordinates(source_coordinates.x, source_coordinates.y + 1), current_cell_above_source, None)

    under_source_neighbors_list = pathfinding.get_current_cell_neighbors(
        Coordinates(source_coordinates.x, source_coordinates.y - 1), current_cell_under_source, None)

    right_source_neighbors_list = pathfinding.get_current_cell_neighbors(
        Coordinates(source_coordinates.x + 1, source_coordinates.y), current_cell_right_source, None)

    lef_sink_neighbors_list = pathfinding.get_current_cell_neighbors(
        Coordinates(sink_coordinates.x - 1, sink_coordinates.y), current_cell_left_sink, None)

    # then
    assert len(above_source_neighbors_list) == 2
    assert len(under_source_neighbors_list) == 2
    assert len(right_source_neighbors_list) == 3
    assert len(lef_sink_neighbors_list) == 3


def test_finding_shortest_way__empty_layout_diagonal_start_and_end_point():
    # given
    production = Production()
    pathfinding = PathFinding(production)
    production.max_coordinate = Coordinates(15, 15)
    production.build_layout()
    start_cell = Cell(Coordinates(2, 2), None)
    end_cell = Cell(Coordinates(9, 9), None)

    # when
    pathfinding.run_a_star_algorithm(start_cell, end_cell, WorkingRobot(1, Coordinates(1, 1), 1, 10))

    # then
    assert len(pathfinding.path_line_list) == 14


def test_finding_shortest_way__layout_diagonal_start_and_end_point_with_three_barrier():
    # given
    production = Production()
    pathfinding = PathFinding(production)
    production.max_coordinate = Coordinates(18, 18)
    production.build_layout()
    start_cell = Cell(Coordinates(2, 2), None)
    end_cell = Cell(Coordinates(15, 16), None)
    test_entity = WorkingRobot(1, Coordinates(1, 1), 1, 10)

    for x in range(5, 18):
        cell = production.get_cell(Coordinates(x, 4))
        cell.placed_entity = WorkingRobot(0, Coordinates(1, 1), 0, 0)

    for x in range(0, 13):
        cell = production.get_cell(Coordinates(x, 8))
        cell.placed_entity = WorkingRobot(0, Coordinates(1, 1), 0, 0)

    for x in range(5, 15):
        cell = production.get_cell(Coordinates(x, 12))
        cell.placed_entity = WorkingRobot(0, Coordinates(1, 1), 0, 0)

    # when
    pathfinding.run_a_star_algorithm(start_cell, end_cell, test_entity)
    v = ProductionVisualisation(production)
    v.visualize_production_layout_in_terminal()

    # then
    assert len(pathfinding.path_line_list) == 27
