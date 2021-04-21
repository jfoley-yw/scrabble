import random
import math
import torch
import os
from dqn.dqn_scrabble_helpers import DQNScrabbleHelpers
from scrabbler.strategy import Strategy

class DQNStrategy(Strategy):
    def __init__(self, model):
        self.model = model

        self.num_actions = 0
        self.action_index_mapping = dict()
        self.index_action_mapping = dict()

        script_path = os.path.dirname(__file__)
        dictionary_path = os.path.join(script_path, '../resources/wwf3/dictionary.txt')
        dictionary_file = open(dictionary_path, 'r')
        for line in dictionary_file:
            self.action_index_mapping[line[:-1]] = self.num_actions
            self.index_action_mapping[self.num_actions] = line[:-1]
            self.num_actions += 1
        dictionary_file.close()

    def choose_move(self, game, rack, score_diff, opponents_rack, dictionary):
        state_vector = DQNScrabbleHelpers.get_state_vector(game.board)
        valid_moves = game.find_valid_moves(rack)
        action_mask = [float('-inf')] * self.num_actions
        for move in valid_moves:
            action_index = self.action_index_mapping[move.word.lower()]
            action_mask[action_index] = 0
        q_values = self.model(state_vector).detach()
        action_mask_vector = torch.tensor([action_mask], dtype = torch.float)
        masked_q_values = q_values + action_mask_vector
        max_q_value = masked_q_values.max(1).indices.item()
        max_word = self.index_action_mapping[max_q_value]
        for move in valid_moves:
            if move.word.lower() == max_word:
                return move
