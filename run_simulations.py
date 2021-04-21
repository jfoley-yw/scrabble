from scrabbler.simulation import Simulation
from scrabbler.player import Player
from scrabbler.strategy import BaselineStrategy
from scrabbler.ABStrategy import ABStrategy
from dqn.dqn_strategy import DQNStrategy
from dqn.dqn_scrabble_helpers import DQNScrabbleHelpers
from dqn.dqn_constants import DQNConstants
from dqn.dqn import DQN
import matplotlib.pyplot as plt
import sys
import torch

def main():
    n = 2
    p0scores = []
    p1scores = []
    # p0endgame_scores = []
    # p1endgame_scores = []

    if len(sys.argv) > 1 and sys.argv[1].startswith("--n="):
        n = int(sys.argv[1][len("--n="):])

    dqn_model = DQN(DQNScrabbleHelpers.calculate_input_size(5), DQNConstants.HIDDEN_LAYER_SIZE, 100)
    dqn_model.load_state_dict(torch.load('./dqn/models/policy_net_final.pt'))
    dqn_strategy = DQNStrategy(dqn_model)
    for i in range(n):
        player0 = Player(dqn_strategy, name="DQN Full-Game")
        player1 = Player(BaselineStrategy(), name="Baseline Full-Game")
        p0score, p1score = Simulation.simulate_game(player0, player1)
        p0scores.append(p0score)
        p1scores.append(p1score)
        # p0endgame_scores.append(p0score - player0.endgame_score)
        # p1endgame_scores.append(p1score - player1.endgame_score)

    colors = []
    numbers = []
    p0_wins = 0
    p1_wins = 0
    for i in range(len(p0scores)):
        numbers.append(i)
        if p0scores[i] > p1scores[i]:
            colors.append("b")
            p0_wins += 1
        elif p1scores[i] > p0scores[i]:
            colors.append("r")
            p1_wins +=1
        else:
            colors.append("k")



    # creates a scatter plot for each game with p1 score on x axis and p2 score on y axis, 
    # blue means p1 wins and red means p2 wins, black means it was a tie 
    xlabel = "Player 1 Score (" + player0.name + ")" 
    ylabel = "Player 2 Score (" + player1.name + ")"
    scatterPlot(p0scores, p1scores, colors, n, xlabel, ylabel)
    
    # creates a line plot of scores with red being p1 and blue being p2 
    plt.plot(numbers, p0scores)
    plt.plot(numbers, p1scores, "r-")
    plt.title("Player1 vs Player 2 Scores")
    plt.show()
    
    # print how many times each player won after n simulations
    print("Player 1 wins: ", p0_wins, "\n Player 2 wins:", p1_wins)


def scatterPlot(p0scores, p1scores, colors, n, xlabel, ylabel):
    plt.scatter(x=p0scores, y=p1scores, c=colors)
    #plt.xlabel()
    #plt.ylabel()
    plt.title("Players' Scores After " + str(n) + " Simulations")
    plt.show()


if __name__ == "__main__":
    main()
