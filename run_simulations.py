from scrabbler.simulation import Simulation
from scrabbler.player import Player
from scrabbler.strategy import BaselineStrategy, RandomStrategy
from scrabbler.ABStrategy import ABStrategy
from dqn.dqn_strategy import DQNStrategy
from dqn.dqn_scrabble_helpers import DQNScrabbleHelpers
from dqn.dqn_constants_4_x_4 import DQNConstants
from dqn.dqn import DQN
import torch
from scrabbler.MCTSStrategy import MCTSStrategy
from scrabbler.ShortMonteCarloSimStrategy import ShortMonteCarloSimStrategy
from scrabbler.PVSStrategy import PVS
import matplotlib.pyplot as plt
import sys
import time

def main():

    n = 1
    p0scores = []
    p1scores = []
    p0endgame_scores = []
    p1endgame_scores = []
    times = []
    nodes = []

    if len(sys.argv) > 1 and sys.argv[1].startswith("--n="):
        n = int(sys.argv[1][len("--n="):])

    # dqn_model = DQN(DQNScrabbleHelpers.calculate_input_size(4), DQNConstants.HIDDEN_LAYER_SIZE, 20)
    # dqn_model.load_state_dict(torch.load('./dqn/models/policy_net_final_4_x_4.pt'))
    # dqn_strategy = DQNStrategy(dqn_model)

    for i in range(n):
        # player0 = Player(dqn_strategy, name="DQN Full-Game")
        # player1 = Player(RandomStrategy(), name="Baseline Full-Game")
        # p0score, p1score = Simulation.simulate_game(player0, player1)
        player1 = Player(ShortMonteCarloSimStrategy(num_rollouts=1500), name="Short Monte Midgame")
        #player1 = Player(MCTSStrategy(num_rollouts=20), name="MCTS strat")
        strategy1 = ABStrategy(reduce_opponent=False)
        player0 = Player(midgame_strategy=BaselineStrategy(), endgame_strategy=strategy1, name="AB Pruning Endgame")
        #player1 = Player(midgame_strategy=BaselineStrategy(), endgame_strategy=BaselineStrategy(), name="Greedy Endgame")
        t0 = time.clock()
        p0score, p1score = Simulation.simulate_game(player0, player1, start_player=0)
        t1 = time.clock() - t0
        p0scores.append(p0score)
        p1scores.append(p1score)
        times.append(t1)
        p0endgame_scores.append(player0.endgame_score)
        p1endgame_scores.append(player1.endgame_score)
        nodes.append( strategy1.total_nodes[0])
        
        print("error")
    print(nodes)


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
    # xlabel = "Player 1 Score (" + player0.name + ")" 
    # ylabel = "Player 2 Score (" + player1.name + ")"
    # scatterPlot(p0scores, p1scores, colors, n, xlabel, ylabel)
    
    # creates a line plot of scores with red being p1 and blue being p2 
    # plt.plot(numbers, p0scores)
    # plt.plot(numbers, p1scores, "r-")
    # plt.title("Player1 vs Player 2 Scores")
    # plt.show()
    
    print("p1 scores", p0scores)
    print("p2 scores", p1scores)
    print("p1 endgame scores", p0endgame_scores)
    print("p2 endgame scores", p1endgame_scores)
    print("times", times)
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
