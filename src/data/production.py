from src.data.cell import Cell


class Production:
    production_layout: list[list[Cell]] = []

    def build_layout(self, max_x_coordinate, max_y_coordinate):
        for y in reversed(range(1, max_y_coordinate)):
            row: list[Cell] = []
            for x in range(1, max_x_coordinate):
                cell = Cell(x, y, None, None, None, False, False)
                row.append(cell)
            self.production_layout.append(row)

    def print_layout(self, max_x_coordinate: int, max_y_coordinate: int):
        print_layout_str = ''

        for y_coordinate, x_coordinate in enumerate(self.production_layout):
            index_variable_y = (max_y_coordinate - 1) - y_coordinate

            if index_variable_y < 10:
                print_layout_str += f'   {index_variable_y}  '
            else:
                print_layout_str += f'  {index_variable_y}  '
            for cell in x_coordinate:
                # elif bedingungen einrücken und die vorher definierten None nicht mehr erwähnen
                if cell.machine is None and cell.transport_robot is None and cell.working_robot is None and cell.source is False and cell.sink is False:
                    print_layout_str += ' \u26AA '
                elif cell.transport_robot is None and cell.working_robot is None and cell.source is False and cell.sink is False:
                    print_layout_str += ' \U0001F534 '
                elif cell.machine is None and cell.transport_robot is not None and cell.working_robot is None and cell.source is False and cell.sink is False:
                    print_layout_str += ' \U0001F7E3 '
                elif cell.machine is None and cell.transport_robot is None and cell.working_robot is not None and cell.source is False and cell.sink is False:
                    print_layout_str += ' \U0001F535 '
                elif cell.machine is None and cell.transport_robot is None and cell.working_robot is None and cell.source is True and cell.sink is False:
                    print_layout_str += ' \U0001F534 '
                elif cell.machine is None and cell.transport_robot is None and cell.working_robot is None and cell.source is False and cell.sink is True:
                    print_layout_str += ' \U0001F534 '
                else:
                    print_layout_str += ' Error '

            print_layout_str += "\n"
        print_layout_str += '      '
        for x in range(1, max_x_coordinate):
            if x < 10 and x % 5 == 0 or x == 1:
                print_layout_str += f'  {x} '
            elif x >= 10 and x % 5 == 0:
                print_layout_str += f' {x} '
            else:
                print_layout_str += (' \u26AB ')
        return print_layout_str

    def print_legend(self):
        print('\u26AA ist ein leeres unbenutzes Feld')
        print('\n \U0001F534 ist eine Maschine ')
        print('\n \U0001F7E3 ist ein Transport Robot')
        print('\n \U0001F535 ist ein Working Robot')
        print('\n \U0001F534 ist die Source (links) und Sink (rechts)')

    def get_source_in_production_layout(self, max_x_coordinate, max_y_coordinate):
        y_coordinate_source = int(max_y_coordinate / 2)

        for y_index, row in enumerate(self.production_layout):
            if y_index == y_coordinate_source:
                cell = row[0]
                cell.source = True
                self.get_cell(0, y_index, max_x_coordinate, max_y_coordinate)
                return cell

    def get_sink_in_production_layout(self, max_x_coordinate, max_y_coordinate):
        y_coordinate_sink = int(max_y_coordinate / 2)
        x_coordinate_sink = int(max_x_coordinate - 2)
        for y_index, row in enumerate(self.production_layout):
            if y_index == y_coordinate_sink:
                cell = row[x_coordinate_sink]
                cell.sink = True
                self.get_cell(0, y_index, max_x_coordinate, max_y_coordinate)
                return cell

    def get_machine_placed_in_production(self):
        pass


    def get_cell(self, x: int, y: int, max_x_coordinate, max_y_coordinate):

        x_true = x
        y_true = max_y_coordinate - y
        cell = self.production_layout[y_true][x_true]

        return cell
