from src.data.order_service import OrderService
from src.data.production import Production


class CommandLineService:
    production = Production()
    order_service = OrderService()

    def create_production(self):
        max_x_coordinate = 2
        max_y_coordinate = 7
        self.production.build_layout(max_x_coordinate, max_y_coordinate)
        self.production.get_source_in_production_layout(max_x_coordinate, max_y_coordinate)
        self.production.get_sink_in_production_layout(max_x_coordinate, max_y_coordinate)

        wr_list = self.create_entities()
        self.production.get_working_robot_placed_in_production(wr_list)

        print(self.production.print_layout(max_x_coordinate, max_y_coordinate))
        print(self.production.print_legend())

    def create_entities(self):
        self.order_service.get_file_production_entities()
        return self.order_service.generate_wr_list()