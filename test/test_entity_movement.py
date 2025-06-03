import pytest

from src.entity.source import Source
from src.entity.working_robot.working_robot import WorkingRobot
from src.production.base.cell import Cell
from src.production.base.coordinates import Coordinates
from src.production.entity_move_serivce import EntityMoveService

from src.production.production import Production


@pytest.mark.parametrize(
    "end_coordinate, path_step_str",
    [
        (Coordinates(6, 5), "6:5"),  # move right
        (Coordinates(4, 5), "4:5"),  # move left
        (Coordinates(5, 6), "5:6"),  # move up
        (Coordinates(5, 4), "5:4"),  # move down
    ]
)
def test_move_entity_one_step__no_obstacle__moved_one_step(mocker, end_coordinate, path_step_str):
    # given
    production_layout = create_testing_layout()

    mock_production: Production = mocker.Mock()
    entity_move_service = EntityMoveService(mock_production)

    mock_wr_working_status = mocker.Mock()
    moving_working_robot = WorkingRobot(1, Coordinates(1, 1), 1, 1, mock_wr_working_status)

    start_cell = Cell(Coordinates(5, 5), moving_working_robot)
    production_layout = place_cell(production_layout, start_cell)

    end_cell = Cell(end_coordinate, None)
    production_layout = place_cell(production_layout, end_cell)

    entity_cell_list = [start_cell]
    mock_production.entities_located = {moving_working_robot.identification_str: entity_cell_list}

    mock_production.get_horizontal_edges_of_coordinates.return_value = (5, 5)
    mock_production.get_vertical_edges_of_coordinates.return_value = (5, 5)

    mock_production.get_cell.side_effect = [end_cell, end_cell, start_cell]

    mock_production.coordinates_in_layout.return_value = True

    # when
    moved_entity_one_step_right = entity_move_service.move_entity_one_step(start_cell, moving_working_robot,
                                                                           path_step_str)

    # then
    assert moved_entity_one_step_right is True
    assert get_cell(production_layout, Coordinates(5, 5)).placed_entity is None
    assert get_cell(production_layout, end_coordinate).placed_entity is moving_working_robot


@pytest.mark.parametrize(
    "end_coordinate, path_step_str",
    [
        (Coordinates(6, 5), "6:5"),  # move right
        (Coordinates(4, 5), "4:5"),  # move left
        (Coordinates(5, 6), "5:6"),  # move up
        (Coordinates(5, 4), "5:4"),  # move down
    ]
)
def test_move_entity_one_step__one_obstacle__moved_no_step(mocker, end_coordinate, path_step_str):
    # given
    production_layout = create_testing_layout()
    obstacle_entity = Source(0, 0, 0)

    mock_production: Production = mocker.Mock()
    entity_move_service = EntityMoveService(mock_production)

    mock_wr_working_status = mocker.Mock()
    moving_working_robot = WorkingRobot(1, Coordinates(1, 1), 1, 1, mock_wr_working_status)

    start_cell = Cell(Coordinates(5, 5), moving_working_robot)
    production_layout = place_cell(production_layout, start_cell)

    end_cell = Cell(end_coordinate, obstacle_entity)
    production_layout = place_cell(production_layout, end_cell)

    entity_cell_list = [start_cell]
    mock_production.entities_located = {moving_working_robot.identification_str: entity_cell_list}

    mock_production.get_horizontal_edges_of_coordinates.return_value = (5, 5)
    mock_production.get_vertical_edges_of_coordinates.return_value = (5, 5)

    mock_production.get_cell.side_effect = [end_cell]

    mock_production.coordinates_in_layout.return_value = True

    # when
    moved_entity_one_step_right = entity_move_service.move_entity_one_step(start_cell, moving_working_robot,
                                                                           path_step_str)

    # then
    assert moved_entity_one_step_right is False
    assert get_cell(production_layout, Coordinates(5, 5)).placed_entity is moving_working_robot
    assert get_cell(production_layout, end_coordinate).placed_entity is obstacle_entity


@pytest.mark.parametrize(
    "start_coordinate, end_coordinate, path_step_str",
    [
        (Coordinates(9, 5), Coordinates(10, 5), "11:5"),  # move right
        (Coordinates(0, 5), Coordinates(-1, 5), "-1:5"),  # move left
        (Coordinates(5, 10), Coordinates(5, 11), "5:11"),  # move up
        (Coordinates(5, 0), Coordinates(5, -1), "5:-1")  # move down
    ]
)
def test_move_entity_one_step__move_out_of_bounds__moved_no_step(mocker, start_coordinate, end_coordinate,
                                                                 path_step_str):
    # given
    production_layout = create_testing_layout()

    mock_production: Production = mocker.Mock()
    entity_move_service = EntityMoveService(mock_production)

    mock_wr_working_status = mocker.Mock()
    moving_working_robot = WorkingRobot(1, Coordinates(1, 1), 1, 1, mock_wr_working_status)

    start_cell = Cell(start_coordinate, moving_working_robot)
    production_layout = place_cell(production_layout, start_cell)

    entity_cell_list = [start_cell]
    mock_production.entities_located = {moving_working_robot.identification_str: entity_cell_list}

    mock_production.get_horizontal_edges_of_coordinates.return_value = (start_coordinate.x, start_coordinate.x)
    mock_production.get_vertical_edges_of_coordinates.return_value = (start_coordinate.y, start_coordinate.y)

    mock_production.get_cell.side_effect = IndexError("Zelle nicht gefunden")

    mock_production.coordinates_in_layout.return_value = True

    # when
    moved_entity_one_step_right = entity_move_service.move_entity_one_step(start_cell, moving_working_robot,
                                                                           path_step_str)

    # then
    assert moved_entity_one_step_right is False
    assert get_cell(production_layout, start_coordinate).placed_entity is moving_working_robot


def create_testing_layout() -> list[list[Cell]]:
    production_layout = []
    for y in reversed(range(0, 10)):
        row: list[Cell] = []
        for x in range(0, 10):
            cell = Cell(Coordinates(x, y), None)
            row.append(cell)
        production_layout.append(row)
    return production_layout


def place_cell(production_layout: list[list[Cell]], new_cell: Cell) -> list[list[Cell]]:
    production_layout[len(production_layout) - 1 - new_cell.cell_coordinates.y][new_cell.cell_coordinates.x] = new_cell
    return production_layout


def get_cell(production_layout: list[list[Cell]], coordinates: Coordinates) -> Cell:
    return production_layout[len(production_layout) - 1 - coordinates.y][coordinates.x]
