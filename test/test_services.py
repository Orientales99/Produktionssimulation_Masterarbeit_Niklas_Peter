from src.entity.machine import Machine
from src.order_data.order import Order
from src.provide_input_data.entity_service import EntityService
from src.provide_input_data.order_service import OrderService
from src.entity.transport_robot import TransportRobot
from src.entity.working_robot import WorkingRobot



def test_wr_list__always__wr_list_is_correct_init(order_service):
    # given
    service_entity = EntityService()

    # when
    wr_list = service_entity.generate_wr_list()

    # then
    assert isinstance(wr_list, list)
    assert len(wr_list) >= 0
    for x in range(0, len(wr_list)):
        assert isinstance(wr_list[x], WorkingRobot)


def test_tr_list__always__wr_list_is_correct_init(order_service):
    # given
    service_entity = EntityService()

    # when
    tr_list = service_entity.generate_tr_list()

    # then
    assert isinstance(tr_list, list)
    assert len(tr_list) >= 0
    for x in range(0, len(tr_list)):
        assert isinstance(tr_list[x], TransportRobot)


def test_machine_list__always__wr_list_is_correct_init():
    # given
    service_entity = EntityService()

    # when
    machine_list = service_entity.generate_machine_list()

    # then
    assert isinstance(machine_list, list)
    assert len(machine_list) >= 0
    for x in range(0, len(machine_list)):
        assert isinstance(machine_list[x], Machine)

def test_order_list__always__order_list_is_correct_init():
    # given
    service_order = OrderService()

    # when
    order_list = service_order.generate_order_list()


    # then
    assert isinstance(order_list, list)
    assert len(order_list) >= 0
    for x in range(0, len(order_list)):
        assert isinstance(order_list[x], Order)