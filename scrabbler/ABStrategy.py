from scrabbler.ABgamestate import ABGamestate
from scrabbler.strategy import Strategy
import copy
import math
from collections import defaultdict



class ABStrategy(Strategy):
    """ A class that represents the AB pruning algorithm"""
    def __init__(self, reduce_opponent=True):
        self.dictionary = None
        self.reduce_opponent = reduce_opponent
        self.search_depth = 2
        self.nodes_visited = 0
        self.total_nodes = []

    def choose_move(self, game, rack, score_diff, opponent_rack, dictionary):
        """Chooses the best move based on the AB-pruning"""
        self.nodes_visited = 0
        self.dictionary = dictionary
        board = copy.deepcopy(game.board)
        gamestate = ABGamestate(board, rack, opponent_rack, 0, score_diff, [])
        value, move = self.minimax(gamestate, self.search_depth, False, -math.inf, math.inf)
        self.total_nodes.append(self.nodes_visited)
        return move
        
    def minimax(self, cur_state, max_depth, is_player_minimizer, alpha, beta):
        """ recursively iterates through the game tree"""
        self.nodes_visited += 1
        best_move = None
        first_move = None
        if max_depth == 0 or cur_state.is_end_state():
            return cur_state.score_diff, cur_state.moves[0]
        
        moves = cur_state.find_next_moves(self.dictionary)

        if len(moves) == 0:
            return cur_state.score_diff, None

        
        if is_player_minimizer:
            
            value = math.inf
            if self.reduce_opponent:
                min_moves = [moves[0]]
            else:
                 min_moves = moves

            for move in min_moves:
                # get the next rack for the minimizing player
                next_rack = cur_state.get_next_rack(move)
                # update the board with the new move, update score differential, and get new gamestate
                next_board = cur_state.get_next_board(move, self.dictionary)
                game_over = (len(next_rack) == 0)
                leaf = max_depth - 1 == 0
                next_score_diff = cur_state.new_score_diff(move.score, game_over, leaf, next_rack)

                moves_to_get_here = cur_state.update_moves(move)
                # create the next state
                next_state = ABGamestate(next_board, cur_state.player_rack, next_rack, is_player_minimizer=False, score_diff=next_score_diff, moves=moves_to_get_here)

                evaluation, first_move = self.minimax(next_state, max_depth - 1, False, alpha , beta)
                value = min(value, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return value, first_move

        if not is_player_minimizer:
            value = -math.inf
            for move in moves:
                # get the next rack for the minimizing player
                next_rack = cur_state.get_next_rack(move)
                # update the board with the new move
                next_board = cur_state.get_next_board(move, self.dictionary)
                # update the score diff
                game_over = (len(next_rack) == 0)
                leaf = max_depth - 1 == 0
                next_score_diff = cur_state.new_score_diff(move.score, game_over, leaf, next_rack)
                # update the moves to get to the gamestate
                moves_to_get_here = cur_state.update_moves(move)
                # create the next state
                next_state = ABGamestate(next_board, next_rack, cur_state.opponent_rack, is_player_minimizer=True, score_diff=next_score_diff, moves=moves_to_get_here)
                
                evaluation, moves_to_here = self.minimax(next_state, max_depth - 1, True, alpha, beta)
                value = max(value, evaluation)
                if max(value, evaluation) is evaluation:
                    value = evaluation 
                    best_move = moves_to_here

                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
                
            return value, best_move
