import pytest

from src.data.machine import Machine
from src.data.order_service import OrderService
from src.data.transport_robot import TransportRobot
from src.data.working_robot import WorkingRobot


@pytest.fixture(autouse=True)
def order_service():
    order_service = OrderService()
    return order_service


def test_wr_list__always__wr_list_is_correct_init(order_service):
    wr_list = order_service.generate_wr_list()
    assert isinstance(wr_list, list)
    assert len(wr_list) >= 0
    for x in range(0, len(wr_list)):
        assert isinstance(wr_list[x], WorkingRobot)


def test_tr_list__always__wr_list_is_correct_init(order_service):
    tr_list = order_service.generate_tr_list()
    assert isinstance(tr_list, list)
    assert len(tr_list) >= 0
    for x in range(0, len(tr_list)):
        assert isinstance(tr_list[x], TransportRobot)


def test_machine_list__always__wr_list_is_correct_init(order_service):
    machine_list = order_service.generate_machine_list()
    assert isinstance(machine_list, list)
    assert len(machine_list) >= 0
    for x in range(0, len(machine_list)):
        assert isinstance(machine_list[x], Machine)

def test_order_list__always__wr_list_is_correct_init(order_service):
    order_list = order_service.generate_order_list()
