from scrabbler.simulation import Simulation
import sys

def main():
    n = 1
    if len(sys.argv) > 1 and sys.argv[1].startswith("--n="):
        n = int(sys.argv[1][len("--n="):])
    for i in range(n):
        Simulation.simulate_game()

if __name__ == "__main__":
    main()
