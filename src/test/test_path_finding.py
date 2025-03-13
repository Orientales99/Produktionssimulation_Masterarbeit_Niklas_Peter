from src.data.cell import Cell
from src.data.coordinates import Coordinates
from src.data.production import Production
from src.data.production_visualisation import ProductionVisualisation
from src.entity_classes.working_robot import WorkingRobot
from src.process_logic.path_finding import PathFinding


def test_neighbors_are_found__around_source_and_sink_after_layout_init():
    # given
    pathfinding = PathFinding()
    production = Production()
    production.create_production()
    source_coordinates = production.source_coordinates
    sink_coordinates = production.sink_coordinates

    # when

    above_source_neighbors_list = pathfinding.get_current_cell_neighbors(
        Coordinates(source_coordinates.x, source_coordinates.y + 1))

    under_source_neighbors_list = pathfinding.get_current_cell_neighbors(
        Coordinates(source_coordinates.x, source_coordinates.y - 1))

    right_source_neighbors_list = pathfinding.get_current_cell_neighbors(
        Coordinates(source_coordinates.x + 1, source_coordinates.y))

    lef_sink_neighbors_list = pathfinding.get_current_cell_neighbors(
        Coordinates(sink_coordinates.x - 1, sink_coordinates.y))

    # then
    assert len(above_source_neighbors_list) == 2
    assert len(under_source_neighbors_list) == 2
    assert len(right_source_neighbors_list) == 3
    assert len(lef_sink_neighbors_list) == 3


def test_finding_shortest_way__empty_layout_diagonal_start_and_end_point():
    # given
    pathfinding = PathFinding()
    production = Production()
    production.max_coordinate = Coordinates(10, 10)
    production.build_layout()
    start_cell = Cell(Coordinates(0, 0), None)
    end_cell = Cell(Coordinates(9, 9,), None)

    # when
    pathfinding.run_a_star_algorithm(start_cell, end_cell)

    # then
    assert len(pathfinding.path_line_list) == 18

def test_finding_shortest_way__layout_diagonal_start_and_end_point_with_three_barrier():
    # given
    pathfinding = PathFinding()
    production = Production()
    production.max_coordinate = Coordinates(10, 10)
    production.build_layout()
    start_cell = Cell(Coordinates(0, 0), None)
    end_cell = Cell(Coordinates(9, 9,), None)
    for x in range(0, 6):
        cell = production.get_cell(Coordinates(x, 3))
        cell.placed_entity = WorkingRobot(0, Coordinates(1,1), 0, 0)

    for x in range(5, 10):
        cell = production.get_cell(Coordinates(x, 5))
        cell.placed_entity = WorkingRobot(0, Coordinates(1,1), 0, 0)

    for x in range(2, 9):
        cell = production.get_cell(Coordinates(x, 7))
        cell.placed_entity = WorkingRobot(0, Coordinates(1,1), 0, 0)


    # when
    pathfinding.run_a_star_algorithm(start_cell, end_cell)
    v = ProductionVisualisation()
    v.visualize_production_layout_in_terminal()

    # then
    assert len(pathfinding.path_line_list) == 22
