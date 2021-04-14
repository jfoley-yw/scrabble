from collections import defaultdict
import copy



class ABGamestate:
    def __init__(self, board, player_rack, opponent_rack, is_player_minimizer, score_diff, moves):
        self.board = board
        self.player_rack = player_rack
        self.opponent_rack = opponent_rack
        self.possible_moves = []
        self.is_player_minimizer = is_player_minimizer
        self.score_diff = score_diff
        self.tiles = {'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3,
         'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10}
        self.moves = moves

    def find_next_moves(self, dictionary):
        if self.is_player_minimizer:
            rack = self.opponent_rack
        else:
            rack = self.player_rack
        across_moves = self.board.find_best_moves(rack, "across", dictionary, self.tiles)
        down_moves = self.board.find_best_moves(rack, "down", dictionary, self.tiles)
        moves = across_moves + down_moves
        # sort so most likely to find best moves first
        moves.sort(key=lambda move_: move_.score, reverse=True)
        return moves[:5]


    def is_end_state(self):
        if len(self.player_rack) == 0 or len(self.opponent_rack) == 0:
            return True

    def new_score_diff(self, move_score):
        if self.is_player_minimizer:
            return self.score_diff - move_score
        
        return self.score_diff + move_score

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
