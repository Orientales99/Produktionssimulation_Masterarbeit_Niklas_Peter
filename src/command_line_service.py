import simpy
from src.data.coordinates import Coordinates
from src.data.order_service import OrderService
from src.data.production import Production
from src.data.simulation_environment import SimulationEnvironment


class CommandLineService:
    production = Production()
    order_service = OrderService()
    simulation_environment = SimulationEnvironment()


    def create_production(self):
        self.order_service.get_files_for_init()
        wr_list = self.order_service.generate_wr_list()
        tr_list = self.order_service.generate_tr_list()
        machine_list = self.order_service.generate_machine_list()
        max_coordinate = self.order_service.set_max_coordinates_for_production_layout()

        self.production.build_layout(max_coordinate)
        self.production.set_source_in_production_layout(max_coordinate)
        self.production.set_sink_in_production_layout(max_coordinate)

        self.production.get_working_robot_placed_in_production(wr_list)
        self.production.get_transport_robot_placed_in_production(tr_list)
        self.production.get_machine_placed_in_production(machine_list, wr_list, tr_list)


        print(self.production.print_layout(max_coordinate))
        print(self.production.print_legend())

    def get_cell_information(self):
        print('From which cell do you require information:')
        more_information = 'y'

        while more_information == 'y':
            x_coordinate = int(input('X:'))
            y_coordinate = int(input('Y: '))
            required_coordinate = Coordinates(x_coordinate, y_coordinate)
            self.production.print_cell_information((required_coordinate))
            more_information = input('Do you need more information? (y/n): ')
        pass
