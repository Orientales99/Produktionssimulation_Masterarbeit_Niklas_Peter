from src.production.base.cell import Cell
from src.constant.constant import MachineQuality, ItemType
from src.production.base.coordinates import Coordinates
from src.entity.machine_storage import MachineStorage
from src.order_data.product import Product
from src.production.production import Production
from src.production.visualisation.production_visualisation import ProductionVisualisation
from src.entity.machine import Machine
from src.entity.working_robot import WorkingRobot


def test_machine_can_drive_right__after_init():
    # given
    production = Production()
    production.max_coordinate = Coordinates(20, 20)
    production.build_layout()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    test_machine = Machine(1,
                           1,
                           MachineQuality.NEW_MACHINE,
                           1,
                           1,
                           Coordinates(1, 1),
                           MachineStorage(100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4)),
                                          100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4))),
                           False,
                           None,
                           1)

    machine_list = [Machine(1,
                            1,
                            MachineQuality.NEW_MACHINE,
                            1,
                            1,
                            Coordinates(1, 1),
                            MachineStorage(100,
                                           Product(
                                               1,
                                               Coordinates(
                                                   1,
                                                   1),
                                               ItemType(
                                                   4)),
                                           100,
                                           Product(
                                               1,
                                               Coordinates(
                                                   1,
                                                   1),
                                               ItemType(
                                                   4))),
                            False,
                            None,
                            1)
                    ]

    production.get_flexible_machine_placed_in_production(machine_list)
    test_machine_id_str = test_machine.identification_str

    machine_coordinates_old = []
    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                machine_coordinates_old.append(cell)

    # when
    production.move_entity_right(test_machine)

    machine_coordinates_new = []

    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                machine_coordinates_new.append(cell)

    updated_machine_coordinates_old = [
        Cell(Coordinates(cell.cell_coordinates.x + 1, cell.cell_coordinates.y), cell.placed_entity)
        for cell in machine_coordinates_old]

    # then
    assert updated_machine_coordinates_old == machine_coordinates_new


def test_machine_can_drive_left__after_init():
    # given
    production = Production()
    production.max_coordinate = Coordinates(20, 20)
    production.build_layout()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    test_machine = Machine(1,
                           1,
                           MachineQuality.NEW_MACHINE,
                           1,
                           1,
                           Coordinates(1, 1),
                           MachineStorage(100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4)),
                                          100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4))),
                           False,
                           None,
                           1)

    machine_list = [Machine(1,
                            1,
                            MachineQuality.NEW_MACHINE,
                            1,
                            1,
                            Coordinates(1, 1),
                            MachineStorage(100,
                                           Product(
                                               1,
                                               Coordinates(
                                                   1,
                                                   1),
                                               ItemType(
                                                   4)),
                                           100,
                                           Product(
                                               1,
                                               Coordinates(
                                                   1,
                                                   1),
                                               ItemType(
                                                   4))),
                            False,
                            None,
                            1)
                    ]

    production.get_flexible_machine_placed_in_production(machine_list)

    machine_coordinates_old = []
    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                machine_coordinates_old.append(cell)

    # when
    production.move_entity_left(test_machine)

    machine_coordinates_new = []

    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                machine_coordinates_new.append(cell)

    updated_machine_coordinates_old = [
        Cell(Coordinates(cell.cell_coordinates.x - 1, cell.cell_coordinates.y), cell.placed_entity)
        for cell in machine_coordinates_old]

    # then
    assert updated_machine_coordinates_old == machine_coordinates_new


def test_machine_can_drive_upwards__after_init():
    # given
    production = Production()
    production.max_coordinate = Coordinates(20, 20)
    production.build_layout()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    test_machine = Machine(1,
                           1,
                           MachineQuality.NEW_MACHINE,
                           1,
                           1,
                           Coordinates(1, 1),
                           MachineStorage(100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4)),
                                          100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4))),
                           False,
                           None,
                           1)

    machine_list = [Machine(1,
                            1,
                            MachineQuality.NEW_MACHINE,
                            1,
                            1,
                            Coordinates(1, 1),
                            MachineStorage(100,
                                           Product(
                                               1,
                                               Coordinates(
                                                   1,
                                                   1),
                                               ItemType(
                                                   4)),
                                           100,
                                           Product(
                                               1,
                                               Coordinates(
                                                   1,
                                                   1),
                                               ItemType(
                                                   4))),
                            False,
                            None,
                            1)
                    ]

    production.get_flexible_machine_placed_in_production(machine_list)

    machine_coordinates_old = []
    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                machine_coordinates_old.append(cell)

    # when
    production.move_entity_upwards(test_machine)

    machine_coordinates_new = []

    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                machine_coordinates_new.append(cell)

    updated_machine_coordinates_old = [
        Cell(Coordinates(cell.cell_coordinates.x, cell.cell_coordinates.y + 1), cell.placed_entity)
        for cell in machine_coordinates_old]

    # then
    assert updated_machine_coordinates_old == machine_coordinates_new


def test_machine_can_drive_downwards__after_init():
    # given
    production = Production()
    production.max_coordinate = Coordinates(20, 20)
    production.build_layout()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    test_machine = Machine(1,
                           1,
                           MachineQuality.NEW_MACHINE,
                           1,
                           1,
                           Coordinates(1, 1),
                           MachineStorage(100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4)),
                                          100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4))),
                           False,
                           None,
                           1)
    machine_list = [Machine(1,
                            1,
                            MachineQuality.NEW_MACHINE,
                            1,
                            1,
                            Coordinates(1, 1),
                            MachineStorage(100,
                                           Product(
                                               1,
                                               Coordinates(
                                                   1,
                                                   1),
                                               ItemType(
                                                   4)),
                                           100,
                                           Product(
                                               1,
                                               Coordinates(
                                                   1,
                                                   1),
                                               ItemType(
                                                   4))),
                            False,
                            None,
                            1)
                    ]
    production.get_flexible_machine_placed_in_production(machine_list)
    machine_coordinates_old = []
    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                machine_coordinates_old.append(cell)

    # when
    production.move_entity_downwards(test_machine)
    machine_coordinates_new = []
    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                machine_coordinates_new.append(cell)
    updated_machine_coordinates_old = [
        Cell(Coordinates(cell.cell_coordinates.x, cell.cell_coordinates.y - 1), cell.placed_entity)
        for cell in machine_coordinates_old]

    # then
    assert updated_machine_coordinates_old == machine_coordinates_new


def test_machine_drives_out_of_the_production_layout__after_init():
    # given
    production = Production()
    production.max_coordinate = Coordinates(20, 20)
    production.build_layout()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    test_machine = Machine(1,
                           1,
                           MachineQuality.NEW_MACHINE,
                           1,
                           1,
                           Coordinates(1, 1),
                           MachineStorage(100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4)),
                                          100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4))),
                           False,
                           None,
                           1)
    machine_list = [test_machine]
    production.get_flexible_machine_placed_in_production(machine_list)
    machine_coordinates_old = []

    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                machine_coordinates_old.append(cell)

    # when
    for a in range(0, 100):
        production.move_entity_downwards(test_machine)

    for b in range(0, 100):
        production.move_entity_right(test_machine)

    for c in range(0, 100):
        production.move_entity_left(test_machine)

    for d in range(0, 9):
        production.move_entity_right(test_machine)

    for e in range(0, 100):
        production.move_entity_upwards(test_machine)

    for f in range(0, 10):
        production.move_entity_downwards(test_machine)

    machine_coordinates_new = []

    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                machine_coordinates_new.append(cell)
    # then

    assert machine_coordinates_old == machine_coordinates_new


def test_wr_drives_to_machine_for_collusion_from_every_side__after_init():
    # given
    production = Production()
    production.max_coordinate = Coordinates(20, 20)
    production.build_layout()
    production.set_sink_in_production_layout()
    production.set_source_in_production_layout()
    test_machine = Machine(1,
                           1,
                           MachineQuality.NEW_MACHINE,
                           1,
                           1,
                           Coordinates(1, 1),
                           MachineStorage(100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4)),
                                          100,
                                          Product(
                                              1,
                                              Coordinates(
                                                  1,
                                                  1),
                                              ItemType(
                                                  4))),
                           False,
                           None,
                           1)
    machine_list = [test_machine]
    test_wr = WorkingRobot(1,
                           Coordinates(1, 1),
                           1,
                           1)
    wr_list = [test_wr]
    production.wr_list = wr_list
    production.get_flexible_machine_placed_in_production(machine_list)
    production.get_working_robot_placed_in_production()
    wr_coordinates_old = []

    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                wr_coordinates_old.append(cell)

    # when
    pv = ProductionVisualisation(production)
    #pv.visualize_layout()

    for x in range(0, 8):
        production.move_entity_right(test_wr)
    #pv.visualize_layout()

    for b in range(0, 100):
        production.move_entity_downwards(test_wr)
    #pv.visualize_layout()

    for c in range(0, 3):
        production.move_entity_right(test_wr)
    #pv.visualize_layout()

    for d in range(0, 2):
        production.move_entity_downwards(test_wr)
    #pv.visualize_layout()

    for e in range(0, 100):
        production.move_entity_left(test_wr)
    #pv.visualize_layout()

    production.move_entity_downwards(test_wr)


    for f in range(0, 2):
        production.move_entity_left(test_wr)
    #pv.visualize_layout()

    for g in range(0, 100):
        production.move_entity_upwards(test_wr)
    #pv.visualize_layout()

    production.move_entity_left(test_wr)
    production.move_entity_upwards(test_wr)
    #pv.visualize_layout()

    for h in range(0, 100):
        production.move_entity_right(test_wr)
    #pv.visualize_layout()

    for i in range(0,3):
        production.move_entity_upwards(test_wr)
    #pv.visualize_layout()

    for j in range(0, 7):
        production.move_entity_left(test_wr)
    wr_coordinates_new = []
    #pv.visualize_layout()

    for index, row in enumerate(production.production_layout):
        for cell in row:
            if cell.placed_entity == Machine:
                wr_coordinates_new.append(cell)


    # then

    assert wr_coordinates_new == wr_coordinates_old


