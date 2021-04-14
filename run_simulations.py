from scrabbler.simulation import Simulation
from scrabbler.player import Player
from scrabbler.strategy import BaselineStrategy
from scrabbler.ABStrategy import ABStrategy
import matplotlib.pyplot as plt
import sys

def main():
    n = 10
    p0scores = []
    p1scores = []

    if len(sys.argv) > 1 and sys.argv[1].startswith("--n="):
        n = int(sys.argv[1][len("--n="):])
    for i in range(n ):
        player1 = Player(midgame_strategy=BaselineStrategy(), endgame_strategy=ABStrategy(), name="AB Pruning Endgame")
        player2 = Player(BaselineStrategy(), name="Greedy Endgame")
        p0score, p1score = Simulation.simulate_game(player1, player2)
        p0scores.append(p0score)
        p1scores.append(p1score)

    colors = []
    p0_wins = 0
    p1_wins = 0
    for i in range(len(p0scores)):
        if p0scores[i] > p1scores[i]:
            colors.append("c")
            p0_wins += 1
        elif p1scores[i] > p0scores[i]:
            colors.append("m")
            p1_wins +=1
        else:
            colors.append("k")
            
    plt.scatter(x=p0scores, y=p1scores, c=colors)
    plt.show()
    plt.xlabel("Player 1 Score (" + player1.name +)
    plt.ylabel("Player 2 Score (" + player2.name +)
    # need to add legend
    plt.title("Players' Scores After " + n + "Simulations")
    print("Player 1 wins: ", p0_wins, "\n Player 2 wins:", p1_wins)


    

if __name__ == "__main__":
    main()
