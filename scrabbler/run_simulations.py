from scrabbler.simulation import Simulation

class RunSimulations:
    @staticmethod
    def run(n):
        for i in range(n):
            Simulation.simulate_game()
