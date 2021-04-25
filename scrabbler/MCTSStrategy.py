import copy
import random
import math

from scrabbler.strategy import Strategy
from collections import defaultdict
from scrabbler.MCTSgamestate import MCTSgamestate

''' Node must be represented by a state of the board/rack/bag-size. dict with those three props
should be used as key for a dict from game state -> reward / attempts'''
class MCTSStrategy(Strategy):
    # LETTERS = ("AAAAAAAAAB"
    #            "BCCDDDDEEE"
    #            "EEEEEEEEEF"
    #            "FGGGHHIIII"
    #            "IIIIIJKLLL"
    #            "LMMNNNNNNO"
    #            "OOOOOOOPPQ"
    #            "RRRRRRSSSS"
    #            "TTTTTTUUUU"
    #            "VVWWXYYZ??")

    LETTERS = ("AAAAAB"
               "BCDEEE"
               "EEE"
               "FGGHIIII"
               "IIJKL"
               "LMNNO"
               "OOOPQ"
               "RRSS"
               "TTUU"
               "VWXYZ")

    RACK_SIZE = 7

    def __init__(self, num_rollouts = 3, explore_factor=1):
        self.num_rollouts = num_rollouts
        self.reward_dict = defaultdict(int)
        self.visits_dict = defaultdict(int)
        self.next_states = {}
        self.dictionary = None
        self.explore_factor = explore_factor
        self.tiles = {'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1,
                         'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
                         'Y': 4, 'Z': 10}
        self.move_between_states = {}

    def choose_move(self, game, rack, current_score_differential, other_rack, dictionary):
        self.other_rack = other_rack  # Ignore this since we cannot know other player's rack
        self.dictionary = dictionary
        tupled_board = tuple(square.tile for square in game.board.get_board())
        tupled_rack = self.tuplify_rack(rack)
        current_game_state = MCTSgamestate(tupled_board, tupled_rack, True, current_score_differential)  # True because it is my turn
        self.board = copy.deepcopy(game.board)
        self.original_board = copy.deepcopy(game.board)
        print('Starting Rollouts: ')
        for i in range(self.num_rollouts):
            self.rollout(current_game_state)
        best_move = self.get_best_move(current_game_state)
        print('Rewards: ', self.reward_dict[current_game_state])
        print('Visits: ', self.visits_dict[current_game_state])
        return best_move

    def deduce_potential_bag(self, tupled_board):
        starting_letters = list(MCTSStrategy.LETTERS)
        for i in range(len(tupled_board)):
            letter = tupled_board[i]
            if letter:
                try:
                    starting_letters.remove(letter)
                except:
                    for j in range(self.board.size):
                        print(tupled_board[j*self.board.size:j*self.board.size+self.board.size])
                    print('The letter: ', letter)
                    raise ValueError
        return starting_letters

    def get_best_move(self, game_state):
        if self.is_terminal(game_state):
            return None

        if game_state not in self.next_states:
            return None

        best_next_state = None
        max_score = float("-inf")
        for state in self.next_states[game_state]:
            if self.visits_dict[state] == 0:
                if max_score == float("-inf"):
                    best_next_state = state
            elif self.reward_dict[state] / self.visits_dict[state] > max_score:
                max_score = self.reward_dict[state] / self.visits_dict[state]
                best_next_state = state
        return self.move_between_states[(game_state, best_next_state)]

    def find_random_sim_child(self, game_state):
        next_states = tuple(self.find_next_states(game_state))
        random_next_state = random.choice(next_states)
        requisite_move = self.move_between_states[(game_state, random_next_state)]
        self.update_board_with_move(self.board, requisite_move)

        return random_next_state

    def tuplify_rack(self, rack):
        char_count = defaultdict(int)
        for char in rack:
            char_count[char] += 1
        all_chars = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','?']
        rack_tuple = tuple(char_count[char] for char in all_chars)
        return rack_tuple

    def rollout(self, game_state):
        path_of_game_states = self.select(game_state)
        final_game_state = path_of_game_states[-1]

        self.expand(final_game_state)

        reward = self.simulate(final_game_state)
        self.backpropagate(path_of_game_states, reward)
        self.board = copy.deepcopy(self.original_board)

    def select(self, game_state):
        path_of_game_states = []
        while True:
            path_of_game_states.append(game_state)
            if game_state not in self.next_states or not self.next_states[game_state]:
                return path_of_game_states
            unexplored_states = self.next_states[game_state].difference(self.next_states.keys())
            if unexplored_states:
                unexplored_state = unexplored_states.pop()
                path_of_game_states.append(unexplored_state)
                requisite_move = self.move_between_states[(game_state, unexplored_state)]
                self.update_board_with_move(self.board, requisite_move)
                return path_of_game_states
            game_state = self.UCT_next_state(game_state)

    def expand(self, game_state):
        if game_state not in self.next_states:
            self.next_states[game_state] = self.find_next_states(game_state)

    def simulate(self, game_state):
        agent_turn = True
        while True:
            if self.is_terminal(game_state):
                score_differential = game_state.score_differential
                if score_differential > 0:
                    reward = 1
                elif score_differential < 0:
                    reward = 0
                else:
                    reward = 0.5
                if agent_turn:
                    return 1 - reward
                return reward

            game_state = self.find_random_sim_child(game_state)
            agent_turn = not agent_turn

    def backpropagate(self, path, reward):
        for game_state in path[::-1]:
        # for game_state in reversed(path):
            self.reward_dict[game_state] += reward
            self.visits_dict[game_state] += 1
            reward = 1 - reward

    def UCT_next_state(self, game_state):
        # Use UCB1 formula to explore and exploit
        best_next_state = None
        max_score = float("-inf")
        for state in self.next_states[game_state]:
            if self.reward_dict[state] / self.visits_dict[state] + self.explore_factor * \
                math.sqrt(math.log(self.visits_dict[game_state]) / self.visits_dict[state]) > max_score:
                max_score = self.reward_dict[state] / self.visits_dict[state] + self.explore_factor * \
                    math.sqrt(math.log(self.visits_dict[game_state]) / self.visits_dict[state])
                best_next_state = state

        requisite_move = self.move_between_states[(game_state, best_next_state)]
        self.update_board_with_move(self.board, requisite_move)
        return best_next_state

    def update_board_with_move(self, current_board, move):
        start_square = move.start_square
        word = move.word
        direction = move.direction
        current_board.place_word(start_square, word, direction)

        # update affected cross sets
        current_board.update_cross_set(start_square, direction, self.dictionary)
        other_direction = "across" if direction == "down" else "down"
        coordinate = start_square
        for _ in word:
            current_board.update_cross_set(coordinate, other_direction, self.dictionary)
            coordinate = current_board.offset(coordinate, direction, 1)

    def find_next_states(self, game_state):
        mid = int(self.board.size / 2)
        curr_rack = self.untuplify_rack(game_state.rack_state)

        if self.board.empty:
            moves = self.board.generate_moves((mid, mid), "across", curr_rack, self.dictionary, self.tiles, {})
        else:
            across_moves = self.board.find_best_moves(curr_rack, "across", self.dictionary, self.tiles)
            down_moves = self.board.find_best_moves(curr_rack, "down", self.dictionary, self.tiles)
            moves = across_moves + down_moves

        next_states = set()

        for move in moves:
            next_board = [square.tile for square in self.board.get_board()]
            index = move.start_square[0] * self.board.size + move.start_square[1]
            for i in range(len(move.word)):
                if move.direction == "across":
                    next_board[index + i] = move.word[i]
                else:
                    next_board[index + i * self.board.size] = move.word[i]
            tupled_board = tuple(next_board)

            curr_bag = self.deduce_potential_bag(tupled_board)
            next_rack = []

            for i in range(min(MCTSStrategy.RACK_SIZE, len(curr_bag))):
                new_letter = random.choice(curr_bag)
                next_rack.append(new_letter)
                curr_bag.remove(new_letter)

            tupled_rack = self.tuplify_rack(next_rack)
            if game_state.is_my_turn:
                next_game_state = MCTSgamestate(tupled_board, tupled_rack, not game_state.is_my_turn, game_state.score_differential + move.score)
            else:
                next_game_state = MCTSgamestate(tupled_board, tupled_rack, not game_state.is_my_turn, game_state.score_differential - move.score)

            next_states.add(next_game_state)

            self.move_between_states[(game_state, next_game_state)] = move
        return next_states

    def is_terminal(self, game_state):
        # check to see if there are no valid moves
        if game_state.rack_state == (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) \
                or not self.has_potential_next_states(game_state):
            return True
        return False

    def has_potential_next_states(self, game_state):
        mid = int(self.board.size / 2)

        curr_rack = self.untuplify_rack(game_state.rack_state)

        if self.board.empty:
            moves = self.board.generate_moves((mid, mid), "across", curr_rack, self.dictionary, self.tiles, {})
        else:
            across_moves = self.board.find_best_moves(curr_rack, "across", self.dictionary, self.tiles)
            down_moves = self.board.find_best_moves(curr_rack, "down", self.dictionary, self.tiles)
            moves = across_moves + down_moves

        if len(moves) > 0:
            return True
        return False

    def untuplify_rack(self, rack_state):
        rack = []
        for i in range(len(rack_state)):
            for j in range(rack_state[i]):
                if i == len(rack_state) - 1:
                    rack.append("?")
                else:
                    rack.append(chr(65 + i))

        return rack
