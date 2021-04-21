import os
from dqn.dqn_simulation import DQNSimulation
from scrabbler.player import Player

class DQNScrabbleObservation:
    def __init__(self, state, actions, action_mask):
        self.state = state
        self.actions = actions
        self.action_mask = action_mask

class DQNScrabbleEnvironment:
    def __init__(self):
        self.simulation = None
        self.num_actions = 0
        self.player = None
        self.current_possible_moves = None

        self.action_index_mapping = dict()

        script_path = os.path.dirname(__file__)
        dictionary_path = os.path.join(script_path, '../resources/wwf5/dictionary.txt')
        dictionary_file = open(dictionary_path, 'r')
        for line in dictionary_file:
            self.action_index_mapping[line[:-1]] = self.num_actions
            self.num_actions += 1
        dictionary_file.close()

    def reset(self):
        self.player = Player(None)
        self.simulation = DQNSimulation(self.player, self.player)
        observation = self.get_observation()
        done = (len(observation.actions) == 0)
        return observation, done

    def step(self, action):
        current_player_score = self.player.get_score()

        move = self.current_possible_moves[action]
        self.simulation.simulate_step(move)

        new_player_score = self.player.get_score()
        reward = new_player_score - current_player_score

        observation = self.get_observation()

        done = (self.simulation.is_rack_empty() or len(observation.actions) == 0)

        return (observation, reward, done)

    def get_final_score(self):
        return self.player.get_score()

    def get_observation(self):
        game = self.simulation.game
        board = game.board
        valid_moves = game.find_valid_moves(self.player.get_rack())

        action_mask = [float('-inf')] * self.num_actions
        actions = []
        self.current_possible_moves = dict()
        for move in valid_moves:
            action_index = self.action_index_mapping[move.word.lower()]
            action_mask[action_index] = 0
            actions.append(action_index)
            self.current_possible_moves[action_index] = move

        return DQNScrabbleObservation(board, actions, action_mask)
