from src.data.production import Production


class CommandLineService:
    production = Production()

    def create_production(self):
        max_x_coordinate = 30
        max_y_coordinate = 30
        self.production.build_layout(max_x_coordinate, max_y_coordinate)
        self.production.get_source_in_production_layout(max_x_coordinate, max_y_coordinate)
        self.production.get_sink_in_production_layout(max_x_coordinate, max_y_coordinate)



        print(self.production.print_layout(max_x_coordinate, max_y_coordinate))
        print(self.production.print_legend())
