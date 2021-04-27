from collections import defaultdict
import copy
import random

class ABGamestate:
    """This class represents a gamestate used as a node in AB Pruning"""
    def __init__(self, board, player_rack, opponent_rack, is_player_minimizer, score_diff, moves):
        self.board = board
        self.player_rack = player_rack
        self.opponent_rack = opponent_rack
        self.possible_moves = []
        self.is_player_minimizer = is_player_minimizer
        self.score_diff = score_diff
        # represents the value associated with each tile
        self.tiles = {'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3,
         'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10}
        self.moves = moves
        # Three options for self.sort_moves: either random, score, or length
        self.sort_moves = None
        # Three options of evalutatoin functions: None (baseline - score diff), "2x" (assume opponent finishes the next turn), and "rack" (incorporates rack heuristics)
        self.eval_function = None


    def find_next_moves(self, dictionary):
        """Finds the next valid moves based on the current gamestate based on the current player"""
        if self.is_player_minimizer:
            rack = self.opponent_rack
        else:
            rack = self.player_rack
        across_moves = self.board.find_best_moves(rack, "across", dictionary, self.tiles)
        down_moves = self.board.find_best_moves(rack, "down", dictionary, self.tiles)
        moves = across_moves + down_moves
        # sort moves based on score (default)
        moves.sort(key=lambda move_: move_.score, reverse=True)
        if self.sort_moves == "random":
            # randomly shuffle moves
            random.shuffle(moves)
        if self.sort_moves == "length":
            moves.sort(key=lambda move_: len(move_.word), reverse=True)
        return moves
            

    def is_end_state(self):
        """ determines if the current gamestate is a terminal state"""
        if len(self.player_rack) == 0 or len(self.opponent_rack) == 0:
            return True

    def new_score_diff(self, move_score, game_over, leaf, new_rack):
        """ finds the score differential after a player makes a move"""
        if self.eval_function == "rack":
            return self.rack_eval(move_score, game_over, leaf, new_rack)
        elif self.eval_function == "2x":
            return self.two_eval(move_score, game_over, leaf, new_rack)
        else:
            return self.baseline_eval(move_score, game_over)


    def baseline_eval(self, move_score, game_over):
        """ Baseline evaluation function"""
        if self.is_player_minimizer:
            new_score = self.score_diff - move_score
            if game_over:
                for tile in self.player_rack:
                    new_score -= 2 * self.tiles[tile] 
        else:
            new_score = self.score_diff + move_score
            if game_over:
                for tile in self.opponent_rack:
                    new_score += 2 * self.tiles[tile]
        return new_score


    def two_eval(self, move_score, game_over, leaf, new_rack):
        """Evaluation function to incentive player's to make moves more quickly"""
        if self.is_player_minimizer:
            new_score = self.score_diff - move_score
            if game_over:
                for tile in self.player_rack:
                    new_score -= 2 * self.tiles[tile]
            elif leaf:
                for tile in new_rack:
                    new_score += 2 * self.tiles[tile]

        else:
            new_score = self.score_diff + move_score
            if game_over:
                for tile in self.opponent_rack:
                    new_score += 2 * self.tiles[tile]
            elif leaf:
                for tile in new_rack:
                    new_score -= 2 * self.tiles[tile]
        return new_score


    def rack_eval(self, move_score, game_over, leaf, new_rack):
        """ Evaluation function that incorporates heuristics of the leftover board"""
        if self.is_player_minimizer:
            new_score = self.score_diff - move_score
            if game_over:
                for tile in self.player_rack:
                    new_score -= 2 * self.tiles[tile]
            elif leaf:
                new_score += self.leftover_rack_heuristics(new_rack)
        else:
            new_score = self.score_diff + move_score
            if game_over:
                for tile in self.opponent_rack:
                    new_score += 2 * self.tiles[tile]
            elif leaf:
                new_score -= self.leftover_rack_heuristics(new_rack)
        return new_score



    def leftover_rack_heuristics(self, rack):
        """ Assesses the value of a leftover rack"""
        score = 0
        # first rack heuristic: duplicate letters are bad
        num_duplicates = len(rack) - len(set(rack))
        score += num_duplicates / len(rack)
        # Q without U heuristic (often challenging to play a Q with no U in the endgame)
        score += self.q_no_u(rack) / len(rack)
        score += self.consonant_vowel_balance(rack) / len(rack)
        return score

    def consonant_vowel_balance(self, rack):
        """Function to determine the consonant to vowel balance of a rack after making a move"""
        vowel = 0
        con = 0
        vowels = ["A", "E", "I", "O", "U"]
        for tile in rack:
            if tile in vowels:
                vowel += 1
            else:
                con += 1
        if con == vowel:
            return 0
        if con > vowel:
            if vowel != 0:
                return con/vowel
            else:
                return con
        if con < vowel:
            if con != 0:
                return vowel/con
            else:
                return vowel


    def q_no_u(self, rack):
        """Determines if a rack has a q and no u"""
        q = False
        u = False
        for tile in rack:
            if tile == "U":
                u = True
            if tile == "Q":
                q == True
        q_no_u = u and q
        if q_no_u:
            return 2
        else:
            return 0
        








    def get_new_rack(self):
        if self.is_player_minimizer:
            return copy.deepcopy(self.opponent_rack)

        return copy.deepcopy(self.player_rack)

    def get_next_rack(self, move):
         # remove the tiles from the players rack
        next_rack = self.get_new_rack()
        start_row = move.start_square[0]
        start_column = move.start_square[1]
        if move.direction == "across":
            for i in range(start_column, start_column + len(move.word)):
                if self.board.square(start_row, i).tile is None:
                    if move.word[i - start_column] not in next_rack:
                        next_rack.remove('?')
                    else:
                        next_rack.remove(move.word[i-start_column])
        else:
            for i in range(start_row, start_row + len(move.word)):
                if self.board.square(i, start_column).tile is None:
                    if move.word[i-start_row] not in next_rack:
                        next_rack.remove('?')
                    else:
                        next_rack.remove(move.word[i-start_row])
        return next_rack

    def update_moves(self, move):
        cur_moves = copy.deepcopy(self.moves)
        return cur_moves + [move]

    def get_next_board(self, move, dictionary):
        next_board = copy.deepcopy(self.board)
        start_square = move.start_square
        word = move.word
        direction = move.direction
        
        next_board.update_cross_set(start_square, direction, dictionary)
        other_direction = "across" if direction == "down" else "down"
        coordinate = start_square
        for _ in word:
            next_board.update_cross_set(coordinate, other_direction, dictionary)
            coordinate = next_board.offset(coordinate, direction, 1)

        return next_board
