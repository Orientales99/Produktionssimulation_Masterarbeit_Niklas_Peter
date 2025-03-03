import pytest

from src.data.machine import Machine
from src.data.order_service import OrderService
from src.data.production import Production
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


@pytest.fixture(autouse=True)
def order_service():
    order_service = OrderService()
    order_service.get_files_for_init()
    return order_service


@pytest.fixture(autouse=True)
def production(order_service):
    max_coordinates = order_service.set_max_coordinates_for_production_layout()
    production = Production()
    production.build_layout(max_coordinates)
    return production


@pytest.fixture(autouse=True)
def wr_list(order_service):
    return order_service.generate_wr_list()


@pytest.fixture(autouse=True)
def tr_list(order_service):
    return order_service.generate_tr_list()


@pytest.fixture(autouse=True)
def machine_list(order_service):
    return order_service.generate_machine_list()


# Test if WR_list is a list, has more than 0 Elements and that the Elements are objective of the Class WorkingRobot
def test_wr_list(wr_list):
    assert isinstance(wr_list, list)
    assert len(wr_list) >= 0
    for x in range(0, len(wr_list)):
        assert isinstance(wr_list[x], WorkingRobot)


# Test if WR_list is a list, has more than 0 Elements and that the Elements are objective of the Class TransportRobot
def test_tr_list(tr_list):
    assert isinstance(tr_list, list)
    assert len(tr_list) >= 0
    for x in range(0, len(tr_list)):
        assert isinstance(tr_list[x], TransportRobot)


# Test if WR_list is a list, has more than 0 Elements and that the Elements are objective of the Class Machine
def test_machine_list(machine_list):
    assert isinstance(machine_list, list)
    assert len(machine_list) >= 0
    for x in range(0, len(machine_list)):
        assert isinstance(machine_list[x], Machine)


# Test: length of the layout is correct init.
def test_build_production_layout(production, order_service):
    max_coordinates = order_service.set_max_coordinates_for_production_layout()
    assert len(production.production_layout) == max_coordinates.y
    for y in range(0, max_coordinates.y):
        assert len(production.production_layout[y]) == max_coordinates.x
