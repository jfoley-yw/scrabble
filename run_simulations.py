from scrabbler.simulation import Simulation
from scrabbler.player import Player
from scrabbler.strategy import BaselineStrategy
import sys

def main():
    n = 1
    if len(sys.argv) > 1 and sys.argv[1].startswith("--n="):
        n = int(sys.argv[1][len("--n="):])
    for i in range(n):
        player1 = Player(BaselineStrategy())
        player2 = Player(BaselineStrategy())
        Simulation.simulate_game(player1, player2)

if __name__ == "__main__":
    main()
