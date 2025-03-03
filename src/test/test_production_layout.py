import pytest

from src.data.coordinates import Coordinates
from src.data.production import Production
from src.data.source import Source


@pytest.fixture(autouse=True)
def production(order_service):
    max_coordinates = order_service.set_max_coordinates_for_production_layout()
    return production


def test__set_source_in_production_layout__always__source_is_in_layout():
    # given
    max_coordinates = Coordinates(100, 100)
    production = Production()
    production.build_layout(max_coordinates)

    # when
    production.set_source_in_production_layout(max_coordinates)

    # then
    assert isinstance(production.get_cell(Coordinates(0, 50)).placed_entity, Source)


# Test: length of the layout is correct init.
def test_build_production_layout(production, order_service):
    max_coordinates = order_service.set_max_coordinates_for_production_layout()
    assert len(production.production_layout) == max_coordinates.y
    for y in range(0, max_coordinates.y):
        assert len(production.production_layout[y]) == max_coordinates.x
