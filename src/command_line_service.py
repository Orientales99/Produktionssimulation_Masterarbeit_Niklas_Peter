from src.data.coordinates import Coordinates
from src.data.order_service import OrderService
from src.data.production import Production


class CommandLineService:
    production = Production()
    order_service = OrderService()

    def create_production(self):
        max_coordinate = Coordinates(30, 30)
        self.production.build_layout(max_coordinate)
        self.production.set_source_in_production_layout(max_coordinate)
        self.production.set_sink_in_production_layout(max_coordinate)

        self.order_service.get_file_production_entities()
        wr_list = self.order_service.generate_wr_list()
        tr_list = self.order_service.generate_tr_list()

        self.production.get_working_robot_placed_in_production(wr_list)
        self.production.get_transport_robot_placed_in_production(tr_list)

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
