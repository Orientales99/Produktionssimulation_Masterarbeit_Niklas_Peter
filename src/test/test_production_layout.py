from src.data.coordinates import Coordinates
from src.data.production import Production
from src.entity_classes.source import Source


def test__set_source_in_production_layout__always__source_is_in_layout():
    # given
    production = Production()
    production.max_coordinate = Coordinates(100, 100)
    production.build_layout()

    # when
    production.set_source_in_production_layout()

    # then
    assert isinstance(production.get_cell(Coordinates(0, 50)).placed_entity, Source)


def test_build_production_layout():
    # given
    production = Production()
    production.max_coordinate = Coordinates(100, 100)

    # when
    production.build_layout()

    # then
    assert len(production.production_layout) == production.max_coordinate.y
    for y in range(0, production.max_coordinate.y):
        assert len(production.production_layout[y]) == production.max_coordinate.x
