import pytest

from src.data.machine import Machine
from src.data.order_service import OrderService
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


@pytest.fixture(autouse=True)
def order_service():
    order_service = OrderService()
    order_service.get_files_for_init()
    return order_service


def test_wr_list(order_service):
    """Test if WR_list is a list, has more than 0 Elements and that the Elements are objective of the Class WorkingRobot"""
    wr_list = order_service.generate_wr_list()
    assert isinstance(wr_list, list)
    assert len(wr_list) >= 0
    for x in range(0, len(wr_list)):
        assert isinstance(wr_list[x], WorkingRobot)


def test_tr_list(order_service):
    """Test if WR_list is a list, has more than 0 Elements and that the Elements are objective of the Class TransportRobot"""
    tr_list = order_service.generate_tr_list()
    assert isinstance(tr_list, list)
    assert len(tr_list) >= 0
    for x in range(0, len(tr_list)):
        assert isinstance(tr_list[x], TransportRobot)


def test_machine_list(order_service):
    """Test if WR_list is a list, has more than 0 Elements and that the Elements are objective of the Class Machine"""
    machine_list = order_service.generate_machine_list()
    assert isinstance(machine_list, list)
    assert len(machine_list) >= 0
    for x in range(0, len(machine_list)):
        assert isinstance(machine_list[x], Machine)
