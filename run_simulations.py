from scrabbler.simulation import Simulation
from scrabbler.player import Player
from scrabbler.strategy import BaselineStrategy
from scrabbler.ABStrategy import ABStrategy
from scrabbler.ShortMonteCarloSimStrategy import ShortMonteCarloSimStrategy
from scrabbler.MCTSStrategy import MCTSStrategy
from scrabbler.RandomStrategy import RandomStrategy
import matplotlib.pyplot as plt
import sys
from collections import defaultdict

def main():
    n = 10
    p0scores = []
    p1scores = []
    p0wins = 0
    p1wins = 0
    # p0endgame_scores = []
    # p1endgame_scores = []
    xletter_to_plays = defaultdict(int)
    xletter_to_points = defaultdict(int)
    if len(sys.argv) > 1 and sys.argv[1].startswith("--n="):
        n = int(sys.argv[1][len("--n="):])
    for i in range(n):
        # player0 = Player(midgame_strategy=BaselineStrategy(), endgame_strategy=ABStrategy(), name="AB Pruning Endgame")
        player1 = Player(ShortMonteCarloSimStrategy(num_rollouts=1000), name="Short Monte Midgame")
        # player0 = Player(MCTSStrategy(num_rollouts=20), name="MCTS strat")
        # player0 = Player(RandomStrategy(), name="Random")
        # player0 = Player(BaselineStrategy(), name="Greedy Endgame")
        player0 = Player(BaselineStrategy(), name="Greedy Endgame")
        p0score, p1score, letters_to_points, letters_to_plays = Simulation.simulate_game(player0, player1)
        p0scores.append(p0score)
        p1scores.append(p1score)
        if p0score > p1score:
            p0wins += 1
        elif p1score > p0score:
            p1wins += 1
        # for letter in letters_to_plays:
        #     xletter_to_plays[letter] += letters_to_plays[letter]
        #     xletter_to_points[letter] += letters_to_points[letter]
        # p0endgame_scores.append(p0score - player0.endgame_score)
        # p1endgame_scores.append(p1score - player1.endgame_score)
    
    # print(xletter_to_plays)
    # print(xletter_to_points)
    # for letter in letters_to_plays:
    #     print(letter, xletter_to_points[letter] / xletter_to_plays[letter])
    return p0scores, p1scores, p0wins, p1wins

    # colors = []
    # numbers = []
    # p0_wins = 0
    # p1_wins = 0
    # for i in range(len(p0scores)):
    #     numbers.append(i)
    #     if p0scores[i] > p1scores[i]:
    #         colors.append("b")
    #         p0_wins += 1
    #     elif p1scores[i] > p0scores[i]:
    #         colors.append("r")
    #         p1_wins +=1
    #     else:
    #         colors.append("k")



    # # creates a scatter plot for each game with p1 score on x axis and p2 score on y axis, 
    # # blue means p1 wins and red means p2 wins, black means it was a tie 
    # xlabel = "Player 1 Score (" + player0.name + ")" 
    # ylabel = "Player 2 Score (" + player1.name + ")"
    # scatterPlot(p0scores, p1scores, colors, n, xlabel, ylabel)
    
    # # creates a line plot of scores with red being p1 and blue being p2 
    # plt.plot(numbers, p0scores)
    # plt.plot(numbers, p1scores, "r-")
    # plt.title("Player1 vs Player 2 Scores")
    # plt.show()
    
    # # print how many times each player won after n simulations
    # print("Player 1 wins: ", p0_wins, "\n Player 2 wins:", p1_wins)


def scatterPlot(p0scores, p1scores, colors, n, xlabel, ylabel):
    plt.scatter(x=p0scores, y=p1scores, c=colors)
    #plt.xlabel()
    #plt.ylabel()
    plt.title("Players' Scores After " + str(n) + " Simulations")
    plt.show()


if __name__ == "__main__":
    # main()
    player0scores, player1scores, p0wins, p1wins = main()
    print('PLAYER 1: \n', player0scores)
    print('PLAYER 2: \n', player1scores)
    print('AVERAGE', sum(player0scores) / len(player0scores),":", sum(player1scores) / len(player1scores))
    print('TOTAL WINS: ', p0wins, ":", p1wins)
