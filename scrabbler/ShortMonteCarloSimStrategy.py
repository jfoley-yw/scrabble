import copy
import random
import math

from scrabbler.strategy import Strategy
from collections import defaultdict


''' Node must be represented by a state of the board/rack/bag-size. dict with those three props
should be used as key for a dict from game state -> reward / attempts'''
class ShortMonteCarloSimStrategy(Strategy):
    # LETTERS = ("AAAAAAAAAB"
    #            "BCCDDDDEEE"
    #            "EEEEEEEEEF"
    #            "FGGGHHIIII"
    #            "IIIIIJKLLL"
    #            "LMMNNNNNNO"
    #            "OOOOOOOPPQ"
    #            "RRRRRRSSSS"
    #            "TTTTTTUUUU"
    #            "VVWWXYYZ")  # TODO - deleted the question marks to remove issue of deducing bag

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

    def __init__(self, num_rollouts = 3, time_limit = 300, exploration_weight=1):
        self.num_rollouts = num_rollouts
        self.time_limit = time_limit  # in seconds # TODO - how to incorporate a time limit
        # self.reward_dict = defaultdict(int)
        # self.visits_dict = defaultdict(int)
        self.next_states = {}
        self.dictionary = None
        self.tiles = {'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1,
                         'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
                         'Y': 4, 'Z': 10}
        # self.move_between_states = {}
        self.num_best_moves = 0
        self.best_moves = []

    def choose_move(self, game, rack, current_score_differential, other_rack, dictionary):  #, is_player1):
        self.board = copy.deepcopy(game.board)
        print('Starting Rollouts: ')
        self.dictionary = dictionary
        self.my_rack = copy.copy(rack)
        self.move_to_score_differential = defaultdict(int)
        self.move_to_visits = defaultdict(int)
        moves = game.find_valid_moves(rack)
        if not moves:
            return None
        num_best_moves = min(len(moves), 10)
        self.best_moves = moves[0:num_best_moves]
        move_index_being_explored = 0
        for i in range(self.num_rollouts):
            self.move_to_visits[self.best_moves[move_index_being_explored]] += 1
            self.move_to_score_differential[self.best_moves[move_index_being_explored]] += current_score_differential
            self.simulate(self.best_moves[move_index_being_explored])
            self.board = copy.deepcopy(game.board)
            move_index_being_explored = (move_index_being_explored + 1) % num_best_moves
        best_move = self.get_best_move()
        # print('Rewards: ', self.reward_dict[current_game_state])
        # print('Visits: ', self.visits_dict[current_game_state])
        return best_move

    def find_plausible_opponent_rack(self, my_rack):
        used_tiles = list(my_rack) + [square.tile for square in self.board.get_board()]
        used_tiles_dict = defaultdict(int)
        for tile in used_tiles:
            used_tiles_dict[tile] += 1

        all_tiles = defaultdict(int)
        for tile in ShortMonteCarloSimStrategy.LETTERS:
            all_tiles[tile] += 1

        potential_letters = []
        for tile in all_tiles:
            for i in range(all_tiles[tile] - used_tiles_dict[tile]):
                potential_letters.append(tile)

        opponent_rack = []
        for i in range(min(ShortMonteCarloSimStrategy.RACK_SIZE, len(potential_letters))):
            added_tile = random.choice(potential_letters)
            opponent_rack += added_tile
            potential_letters.remove(added_tile)

        return opponent_rack

    def get_refilled_rack(self, my_rack):
        used_tiles = list(my_rack) + [square.tile for square in self.board.get_board()]
        used_tiles_dict = defaultdict(int)
        for tile in used_tiles:
            used_tiles_dict[tile] += 1

        all_tiles = defaultdict(int)
        for tile in ShortMonteCarloSimStrategy.LETTERS:
            all_tiles[tile] += 1

        potential_letters = []
        for tile in all_tiles:
            for i in range(all_tiles[tile] - used_tiles_dict[tile]):
                potential_letters.append(tile)

        next_rack = []
        for i in range(min(ShortMonteCarloSimStrategy.RACK_SIZE, len(potential_letters))):
            added_tile = random.choice(potential_letters)
            next_rack += added_tile
            potential_letters.remove(added_tile)

        return next_rack

    # TODO - if i am player 1 then add to score differential, otherwise subtract from score differential
    # TODO - make sure that if i am player 1 we choose move with high score differentail and otherwise choose low score differential

    def simulate(self, move):
        self.current_initial_move = move
        start_square = move.start_square
        word = move.word
        direction = move.direction

        # Remove tiles from my rack and then refill
        my_rack = copy.deepcopy(self.my_rack)
        start_row = start_square[0]
        start_column = start_square[1]
        if move.direction == "across":
            for i in range(start_column, start_column + len(move.word)):
                if self.board.square(start_row, i).tile is None:
                    if move.word[i - start_column] not in my_rack:
                        my_rack.remove('?')
                    else:
                        my_rack.remove(move.word[i - start_column])
        else:
            for i in range(start_row, start_row + len(move.word)):
                if self.board.square(i, start_column).tile is None:
                    if move.word[i - start_row] not in my_rack:
                        my_rack.remove('?')
                    else:
                        my_rack.remove(move.word[i - start_row])

        # place move on board
        self.board.place_word(start_square, word, direction)

        # update affected cross sets
        self.board.update_cross_set(start_square, direction, self.dictionary)
        other_direction = "across" if direction == "down" else "down"
        coordinate = start_square
        for _ in word:
            self.board.update_cross_set(coordinate, other_direction, self.dictionary)
            coordinate = self.board.offset(coordinate, direction, 1)

        self.move_to_score_differential[self.current_initial_move] += move.score
        # if self.is_my_turn:
        #     self.move_to_score_differential[self.current_initial_move] += move.score
        # else:
        #     self.move_to_score_differential[self.current_initial_move] -= move.score

        my_new_rack = self.get_refilled_rack(my_rack)

        self.simulate_opponent_move(my_new_rack)

    def simulate_opponent_move(self, my_rack):
        # set up opponent's plausible next rack
        opponent_rack = self.find_plausible_opponent_rack(my_rack)

        across_moves = self.board.find_best_moves(opponent_rack, "across", self.dictionary, self.tiles)
        down_moves = self.board.find_best_moves(opponent_rack, "down", self.dictionary, self.tiles)
        moves = across_moves + down_moves

        if not moves:
            return

        # move = random.choice(moves)
        move = moves[0]  # TODO - not random simulation but logic move instead

        start_square = move.start_square
        word = move.word
        direction = move.direction

        # Remove used letters from opponent rack
        start_row = start_square[0]
        start_column = start_square[1]
        if move.direction == "across":
            for i in range(start_column, start_column + len(move.word)):
                if self.board.square(start_row, i).tile is None:
                    if move.word[i - start_column] not in opponent_rack:
                        opponent_rack.remove('?')
                    else:
                        opponent_rack.remove(move.word[i - start_column])
        else:
            for i in range(start_row, start_row + len(move.word)):
                if self.board.square(i, start_column).tile is None:
                    if move.word[i - start_row] not in opponent_rack:
                        opponent_rack.remove('?')
                    else:
                        opponent_rack.remove(move.word[i - start_row])

        # place move on board
        self.board.place_word(start_square, word, direction)

        # update affected cross sets
        self.board.update_cross_set(start_square, direction, self.dictionary)
        other_direction = "across" if direction == "down" else "down"
        coordinate = start_square
        for _ in word:
            self.board.update_cross_set(coordinate, other_direction, self.dictionary)
            coordinate = self.board.offset(coordinate, direction, 1)

        self.move_to_score_differential[self.current_initial_move] -= move.score
        # if self.is_my_turn:
        #     self.move_to_score_differential[self.current_initial_move] -= move.score
        # else:
        #     self.move_to_score_differential[self.current_initial_move] += move.score

        self.simulate_my_final_move(my_rack)

    def simulate_my_final_move(self, my_rack):
        across_moves = self.board.find_best_moves(my_rack, "across", self.dictionary, self.tiles)
        down_moves = self.board.find_best_moves(my_rack, "down", self.dictionary, self.tiles)
        moves = across_moves + down_moves

        if not moves:
            return

        # move = random.choice(moves)
        move = moves[0]  # TODO - not random simulation but logic move instead

        self.move_to_score_differential[self.current_initial_move] += move.score
        # if self.is_my_turn:
        #     self.move_to_score_differential[self.current_initial_move] += move.score
        # else:
        #     self.move_to_score_differential[self.current_initial_move] -= move.score

    def get_best_move(self):
        return max(self.move_to_score_differential.keys(), key = lambda move: self.move_to_score_differential[move] / self.move_to_visits[move])
        # if self.is_player1:
        #     return max(self.move_to_score_differential.keys(), key = lambda move: self.move_to_score_differential[move] / self.move_to_visits[move])
        # else:
        #     return min(self.move_to_score_differential.keys(), key = lambda move: self.move_to_score_differential[move] / self.move_to_visits[move])

