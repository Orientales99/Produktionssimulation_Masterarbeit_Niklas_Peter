from matplotlib import pyplot as plt

from src.data.coordinates import Coordinates
from src.data.order_service import OrderService
from src.data.production import Production
from src.data.simulation_environment import SimulationEnvironment


class CommandLineService:
    production = Production()
    order_service = OrderService()
    simulation_environment = SimulationEnvironment()

    def create_production(self):

        max_coordinate = self.order_service.set_max_coordinates_for_production_layout()

        self.production.create_production(max_coordinate)
        self.production.set_entities(wr_list, tr_list, machine_list)


        if self.order_service.set_visualising_via_matplotlib() == True:
            self.visualize_production_layout_in_matplotlib(max_coordinate)

        if self.order_service.set_visualising_via_terminal() == True:
            self.visualize_production_layout_in_terminal(max_coordinate)

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

    def visualize_production_layout_in_matplotlib(self, max_coordinate):
        grid = self.production.print_layout_as_a_field_in_extra_tab(max_coordinate)
        fig, ax = plt.subplots()
        info_text = ax.text(0.95, 0.05, '', transform=ax.transAxes, fontsize=12,
                            verticalalignment='bottom', horizontalalignment='right', color='black')
        fig.canvas.mpl_connect('motion_notify_event',
                               lambda event: self.production.hover_for_cell_information(event, info_text))

        plt.imshow(grid, origin='lower')
        plt.show()

    def visualize_production_layout_in_terminal(self, max_coordinate):
        print(self.production.print_layout_in_command_box(max_coordinate))
        print(self.production.print_legend())
        self.get_cell_information()
