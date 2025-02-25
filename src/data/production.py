from src.data.cell import Cell


class Production:
    production_layout: list[list[Cell]] = []

    def build_layout(self, max_x_coordinate, max_y_coordinate):
        for y in reversed(range(1, max_y_coordinate)):
            row: list[Cell] = []
            for x in range(1, max_x_coordinate):
                cell = Cell(x, y, None, None, None, None, None)
                row.append(cell)
            self.production_layout.append(row)

    def print_layout(self, max_x_coordinate, max_y_coordinate):
        print_layout_str = ''

        for y_coordinate, x_coordinate in enumerate(self.production_layout):
            index_variable_y = (max_y_coordinate - 1 ) - y_coordinate

            if index_variable_y < 10:
                print_layout_str += f'   {index_variable_y}  '
            else:
                print_layout_str += f'  {index_variable_y}  '
            for cell in x_coordinate:
                if cell.machine is None and cell.transport_robot is None and cell.working_robot is None:
                    print_layout_str += ' \u26AA '
                elif cell.machine is not None and cell.transport_robot is None and cell.working_robot is None:
                    print_layout_str += ' \U0001F534 '
                elif cell.machine is None and cell.transport_robot is not None and cell.working_robot is None:
                    print_layout_str += ' \U0001F7E3 '
                elif cell.machine is None and cell.transport_robot is None and cell.working_robot is not None:
                    print_layout_str += ' \U0001F535 '
                else:
                    print_layout_str += ' Error '

            print_layout_str += "\n"
        print_layout_str += '      '
        for x in range(1, max_x_coordinate):
            if x < 10 and x % 5 == 0:
                print_layout_str += f'  {x} '
            elif x >= 10 and x % 5 == 0:
                print_layout_str += f' {x} '
            else:
                print_layout_str += (' \u26AB ')
        return print_layout_str

    def print_legend(self):
        print('\u26AA ist ein leeres unbenutzes Feld')
        print('\U0001F534 ist eine Maschine ')
        print('\U0001F7E3 ist ein Transport Robot')
        print('\U0001F535 ist ein Working Robot')
        print(' "\U0001F7E1" is die Source')

    def get_source_in_production_layout(self, max_y_coordinate):
        y_coordinate_source = max_y_coordinate/2

        for y_coordinate, x_coordinate in enumerate(self.production_layout):
                if y_coordinate_source == y_coordinate:
                    # cell.x_coordinate(1)
                    pass