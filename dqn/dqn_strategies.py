import random
import math
from dqn.dqn_helpers import DQNHelpers
from scrabbler.strategy import Strategy

class DQNStrategy(Strategy):
    def __init__(self, model):
        self.model = model

    def policy(self, game, rack):
        valid_moves = game.find_valid_moves(rack)
        max_q_value = float('-inf')
        max_action = None
        for move in valid_moves:
            q_value = self.model(DQNHelpers.get_input_vector(game, move.word)).item()
            if q_value > max_q_value:
                max_q_value = q_value
                max_action = move
        return max_action

class DQNTrainingStrategy(DQNStrategy):
    def __init__(self, model, eps_start, eps_end, eps_decay):
        super().__init__(model)
        self.eps_start = eps_start
        self.eps_end = eps_end
        self.eps_decay = eps_decay
        self.steps_done = 0

    # inspired by https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
    def choose_move(self, game, rack):
        sample = random.random()
        eps_threshold = self.eps_end + (self.eps_start - self.eps_end) * \
            math.exp(-1. * self.steps_done / self.eps_decay)
        self.steps_done += 1
        if sample > eps_threshold:
            return self.policy(game, rack)
        else:
            valid_moves = game.find_valid_moves(rack)
            return valid_moves[random.randrange(len(valid_moves))]

class DQNPlayingStrategy(DQNStrategy):
    def choose_move(self, game, rack):
        return self.policy(game, rack)
