import random
import math
import torch
from dqn.dqn_helpers import DQNHelpers
from scrabbler.strategy import Strategy

class DQNStrategy(Strategy):
    def __init__(self, model):
        self.model = model

    def choose_move(self, game, rack, score_diff, opponents_rack, dictionary):
        # choose a move
