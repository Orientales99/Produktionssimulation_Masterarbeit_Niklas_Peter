import simpy


class SimulationEnvironment:
    def __init__(self):
        self.env = simpy.Environment()

    def run_simulation(self, until: int):
        self.env.run(until=until)
