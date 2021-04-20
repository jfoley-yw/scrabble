from dqn.dqn_simulation import DQNSimulation
from scrabbler.player import Player

class DQNScrabbleObservation:
    def __init__(self, state, action_mask):
        self.state = state
        self.action_mask = action_mask

class DQNScrabbleEnvironment:
    def __init__(self):
        self.simulation = None
        self.num_actions = 0
        self.player = None
        self.current_possible_moves = None

        self.action_index_mapping = dict()
        self.index_action_mapping = dict()
        dictionary_path = '../resources/wwf5/dictionary.txt'
        dictionary_file = open(dictionary_path, 'r')
        for line in dictionary_file:
            self.action_index_mapping[line[:-1]] = self.num_actions
            self.index_action_mapping[self.num_actions] = line[:-1]
            self.num_actions += 1
        dictionary_file.close()

    def reset(self):
        self.player = Player(None)
        self.simulation = DQNSimulation(player, player)
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

        return (observation, reward, done, None)

    def get_final_score():
        return self.player.get_score()

    def get_observation(self):
        game = self.simulation.game
        board = game.board
        valid_moves = game.find_valid_moves(self.player.rack())

        action_mask = [float('-inf')] * self.num_actions
        self.current_possible_moves = dict()
        for move in valid_moves:
            action_index = self.action_index_mapping[move.word]
            action_mask[action_index] = 1
            self.current_possible_moves[action_index] = move

        return DQNScrabbleObservation(board, action_mask)
