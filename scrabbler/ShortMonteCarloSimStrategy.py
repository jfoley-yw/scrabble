import copy
import random
import math

from scrabbler.strategy import Strategy
from collections import defaultdict


''' Represents an implementation of an algorithm based on the Maven and Scrabble bots for the
    Scrabble midgame. It utilizes a static evaluation function with several heuristics, simulation
    2-ply deep, and pruning of moves based on standard deviation of each move's average simualted 
    future-game score differentials.
'''
class ShortMonteCarloSimStrategy(Strategy):
    # Relative letter utilities calculated based off of simulating thousands of games. Once a letter
    # was placed in a game, the future score differential was tracked and used to calculate utilities,
    # as described in Maven implementation. 
    ESTIMATED_LETTER_UTILITY = {"A": 15.75, "B": 17.41, "C": 16.64, "D": 15.54, "E": 15.10, "F": 17.22, 
                                "G": 15.66, "H": 15.81, "I": 15.92, "J": 21.71, "K": 17.95, "L": 13.50, 
                                "M": 17.20, "N": 15.17, "O": 16.76, "P": 18.26, "Q": 20.26, "R": 13.28, 
                                "S": 13.74, "T": 15.38, "U": 16.40, "V": 16.39, "W": 16.66, "X": 21.08, 
                                "Y": 16.29, "Z": 23.14}

    # Used in calculation of the heuristic for ratio of vowels to consonants
    VOWELS = ["A", "E", "I", "O", "U", "Y"]

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

    ''' Initialize strategy with the number of rollouts to do, the exploration weight, map of 
        states->child states, map of tiles->value, and an empty list of the current best moves.
    '''
    def __init__(self, num_rollouts = 1000, exploration_weight=1):
        self.num_rollouts = num_rollouts
        self.next_states = {}
        self.dictionary = None
        self.tiles = {'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1,
                         'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
                         'Y': 4, 'Z': 10}
        self.num_best_moves = 0
        self.best_moves = []

    ''' Choose the estimated best move by using a static evaluation function and performing simulations.
    '''
    def choose_move(self, game, rack, current_score_differential, other_rack, dictionary):
        self.board = copy.deepcopy(game.board)
        print('Starting Rollouts: ')
        self.dictionary = dictionary
        self.my_rack = copy.copy(rack)
        self.move_to_score_differential = {}
        self.move_to_visits = defaultdict(int)

        moves = game.find_valid_moves(self.my_rack)
        if not moves:
            return None
        num_moves = min(len(moves), 30)
        self.best_moves = self.static_evaluation(moves[0:num_moves], self.my_rack)
        return self.do_rollouts(game)

    ''' Determine the best moves from all possible moves based on several heuristics.
    '''
    def static_evaluation(self, moves, rack):
        static_value = defaultdict(int)
        highest_score = moves[0].score
        for move in moves:
            # Heuristic 1: Score
            static_value[move] += move.score

            # Heuristic 2: leftover rack value (leftover tiles values + potential tile values in bag)
            leftover_rack = copy.deepcopy(rack)
            start_square = move.start_square
            start_row = start_square[0]
            start_column = start_square[1]
            if move.direction == "across":
                for i in range(start_column, start_column + len(move.word)):
                    if self.board.square(start_row, i).tile is None:
                        leftover_rack.remove(move.word[i - start_column])
            else:
                for i in range(start_row, start_row + len(move.word)):
                    if self.board.square(i, start_column).tile is None:
                        leftover_rack.remove(move.word[i - start_row])
            for char in leftover_rack:
                static_value[move] += ShortMonteCarloSimStrategy.ESTIMATED_LETTER_UTILITY[char] * highest_score * 0.0003
            static_value[move] += self.unseen_tiles_value(move, rack) * highest_score * 0.03
            
            # Heuristic 3: value:consonants ratio closer to 1
            vowels = 0
            for tile in leftover_rack:
                if tile in ShortMonteCarloSimStrategy.VOWELS:
                    vowels += 1
            if vowels == 0 or vowels == len(leftover_rack):
                ratio = 0
            elif len(leftover_rack) < 2 * vowels:
                ratio = vowels / (len(leftover_rack) - vowels)
            else:
                ratio = (len(leftover_rack) - vowels) / vowels

            static_value[move] += math.sqrt(ratio) * highest_score * 0.004  

            # Heuristic 4: U-with-Q-unseen
            if self.is_Q_in_unseen(move, rack) and "U" in leftover_rack:
                static_value[move] += highest_score * 0.002
            
            # Heuristic 5: First turn places fewer tiles
            if self.board.empty:
                static_value[move] += (1 / len(move.word)) * highest_score * 0.02
        sorted_moves = sorted(moves, key= lambda move: static_value[move], reverse=True)
        num_moves = min(3, len(moves))
        return sorted_moves[0:num_moves]

    ''' Check to see if there might be a Q tile in the bag. It cannot be known for sure if a Q tile
        is in the opponent's rack or in the bag, just that it has a chance of being in the bag.
    '''          
    def is_Q_in_unseen(self, move, rack):
        used_tiles = list(rack) + [square.tile for square in self.board.get_board()]
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
        if "Q" in potential_letters:
            return True

    ''' Calculate the average value of tiles that might be in the bag, for the purposes of estimating
        how good a leftover rack might be.
    '''
    def unseen_tiles_value(self, move, rack):
        used_tiles = list(rack) + [square.tile for square in self.board.get_board()]
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

        unseen_value = 0
        for tile in potential_letters:
            unseen_value += ShortMonteCarloSimStrategy.ESTIMATED_LETTER_UTILITY[tile]
        average_val = 0.01 * unseen_value / len(potential_letters)
        return average_val * min(ShortMonteCarloSimStrategy.RACK_SIZE - len(move.word), len(potential_letters))

    ''' Simulate 2-ply into the future to estimate the average score differential assocaited with a
        move. 17 iterations are performed for each move, then for subsequent iterations, any moves 
        with a score differential not within 2 standard deviations of the highest score differential is
        pruned from the list of moves being considered. Simulations are carried out until one move 
        statistically distances itself from all other moves or until the allotted number of rollouts is
        reached.
    '''
    def do_rollouts(self, game):
        # after 17 iterations through each move, start pruning anything not within 2 standard deviations
        rollouts_left = self.num_rollouts
        moves_under_consideration = self.best_moves
        if len(moves_under_consideration) == 1:
            return moves_under_consideration[0]
        is_after_17_rollouts_each = False
        current_move_index = 0
        for i in range(self.num_rollouts):
            self.move_to_visits[moves_under_consideration[current_move_index]] += 1
            if moves_under_consideration[current_move_index] not in self.move_to_score_differential:
                self.move_to_score_differential[moves_under_consideration[current_move_index]] = 0
            self.simulate(moves_under_consideration[current_move_index])
            self.board = copy.deepcopy(game.board)

            current_move_index = (current_move_index + 1) % len(moves_under_consideration)
            if not is_after_17_rollouts_each and (i / len(moves_under_consideration)) >= 17:
                is_after_17_rollouts_each = True
            if current_move_index == 0 and is_after_17_rollouts_each:
                moves_under_consideration = self.remove_poor_words(moves_under_consideration)
                if len(moves_under_consideration) == 1:
                    return moves_under_consideration[0]

        return max(moves_under_consideration, key = lambda move: self.move_to_score_differential[move] / self.move_to_visits[move])

    ''' Remove any words whose average future score differential is not within 2 standard deviations of
        the highest future score differential.
    '''
    def remove_poor_words(self, moves):
        new_moves = []
        current_max = float("-inf")
        total_points = 0
        all_same_score = True
        for move in moves:
            if not (self.move_to_score_differential[moves[0]] == self.move_to_score_differential[move]):
                all_same_score = False
                break
        if all_same_score:
            return [moves[0]]

        for move in moves:
            total_points += self.move_to_score_differential[move]

        # Calculate standard deviation
        average = total_points / len(moves)
        diff_summation = 0
        for move in moves:
            diff_summation += (self.move_to_score_differential[move] - average) ** 2
        standard_deviation = math.sqrt(diff_summation / len(moves))

        for move in moves:
            current_max = max(current_max, self.move_to_score_differential[move])
        
        for move in moves:
            if current_max - self.move_to_score_differential[move] < (2 * standard_deviation):
                new_moves.append(move)
        return new_moves

    ''' Create a random rack for the opponent during simulation that could plausibly exist given
        one's own rack and the tiles that have already been played on the board.
    '''
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

    ''' Refill agent's own rack after a move with tiles that are potentially in the bag based on
        what tiles have already been played.
    '''
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

    ''' Start the simulation from a move to 2-ply forward in the game. The move is placed on the board,
        the agent's rack is refilled, and we move on to the opponent's simualted move.
    '''
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
        my_new_rack = self.get_refilled_rack(my_rack)
        self.simulate_opponent_move(my_new_rack)

    ''' Simulate the opponent's move given that the agent has just placed a word on the board and
        refilled their rack. '''
    def simulate_opponent_move(self, my_rack):
        # set up opponent's plausible next rack
        opponent_rack = self.find_plausible_opponent_rack(my_rack)

        across_moves = self.board.find_best_moves(opponent_rack, "across", self.dictionary, self.tiles)
        down_moves = self.board.find_best_moves(opponent_rack, "down", self.dictionary, self.tiles)
        moves = across_moves + down_moves

        if not moves:
            return

        move = moves[0]  # Not random simulation but logical move instead

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

        # Since opponent made move, subtract their word's score from our score differential
        self.move_to_score_differential[self.current_initial_move] -= move.score

        self.simulate_my_final_move(my_rack)
    
    ''' Simulate agent's final move and add move's score to score differential for the associated
        original move.
    '''
    def simulate_my_final_move(self, my_rack):
        across_moves = self.board.find_best_moves(my_rack, "across", self.dictionary, self.tiles)
        down_moves = self.board.find_best_moves(my_rack, "down", self.dictionary, self.tiles)
        moves = across_moves + down_moves
        if not moves:
            return
        move = moves[0] # Not random simulation but logical move instead
        self.move_to_score_differential[self.current_initial_move] += move.score

    ''' Return the best move from the current game state. The best move has the highest average
        score differential from its simulations.
    '''
    def get_best_move(self):
        return max(self.move_to_score_differential.keys(), key = lambda move: self.move_to_score_differential[move] / self.move_to_visits[move])
