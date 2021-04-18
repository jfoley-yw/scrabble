import random
import math
import torch
from dqn.dqn_helpers import DQNHelpers
from scrabbler.strategy import Strategy

class DQNStrategy(Strategy):
    def __init__(self, model):
        self.model = model

    def policy(self, game, rack):
        valid_moves = game.find_valid_moves(rack)
        if len(valid_moves) == 0:
            return None
        input_vectors = [DQNHelpers.get_input_vector(game, move.word) for move in valid_moves]
        with torch.no_grad():
            q_values = self.model(torch.cat(input_vectors, 0))
        max_action_index = q_values.max(0).indices.item()
        return valid_moves[max_action_index]

class DQNTrainingStrategy(DQNStrategy):
    STEPS_DONE = 0

    def __init__(self, model, eps_start, eps_end, eps_decay):
        super().__init__(model)
        self.eps_start = eps_start
        self.eps_end = eps_end
        self.eps_decay = eps_decay

    # inspired by https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
    def choose_move(self, game, rack, score_diff, opponents_rack, dictionary):
        sample = random.random()
        eps_threshold = self.eps_end + (self.eps_start - self.eps_end) * \
            math.exp(-1. * DQNTrainingStrategy.STEPS_DONE / self.eps_decay)
        DQNTrainingStrategy.STEPS_DONE += 1
        if sample > eps_threshold:
            return self.policy(game, rack)
        else:
            valid_moves = game.find_valid_moves(rack)
            if len(valid_moves) == 0:
                return None
            return valid_moves[random.randrange(len(valid_moves))]

class DQNPlayingStrategy(DQNStrategy):
    def choose_move(self, game, rack, score_diff, opponents_rack, dictionary):
        return self.policy(game, rack)
