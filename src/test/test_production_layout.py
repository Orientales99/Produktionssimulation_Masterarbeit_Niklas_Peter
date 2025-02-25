from unittest import TestCase
from src.data.production import Production


class TestProductionLayout(TestCase):
    def test_build_layout(self):
        production = Production()
        production.build_layout()
        assert len(production.production_layout) >= 29
        for index in range(0, 29):
            assert len(production.production_layout[index]) >= 29

