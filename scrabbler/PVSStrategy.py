from scrabbler.ABgamestate import ABGamestate
from scrabbler.strategy import Strategy
import copy
import math
from collections import defaultdict


class PVS(Strategy):
    def __init__(self, reduce_opponent=False):
        self.dictionary = None
        self.reduce_opponent = reduce_opponent
        self.num_times_wrong = 0
        self.nodes_visited = 0
        self.total_nodes = []

    def choose_move(self, game, rack, score_diff, opponent_rack, dictionary):
        self.nodes_visited = 0
        self.dictionary = dictionary
        board = copy.deepcopy(game.board)
        gamestate = ABGamestate(board, rack, opponent_rack, 0, score_diff, [])
        value, move = self.pvs(gamestate, 100, False, -math.inf, math.inf)
        self.total_nodes.append(self.nodes_visited)
        return move
        
        
    def pvs(self, cur_state, max_depth, is_player_minimizer, alpha, beta):
        self.nodes_visited += 1
        best_move = None
        first_move = None
        if max_depth == 0 or cur_state.is_end_state():
            return cur_state.score_diff, cur_state.moves[0]
        
        moves = cur_state.find_next_moves(self.dictionary, )
        if len(moves) == 0:
            return cur_state.score_diff, None
        
        if is_player_minimizer:
            
            value = math.inf
            if self.reduce_opponent:
                min_moves = [moves[0]]
            else:
                 min_moves = moves

            ind = 0
            re_search = False
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
                
                if ind == 0 or re_search:
                    evaluation, first_move = self.pvs(next_state, max_depth - 1, False, alpha , beta)
                    value = min(value, evaluation)
                    beta = min(beta, evaluation)

                else:
                    evaluation, first_move = self.pvs(next_state, max_depth - 1, False, alpha , beta)
                    # value = min(value, evaluation)
                    # print("evaluation", evaluation)
                    # print("beta", beta)
                    if evaluation > beta:
                        re_search = True
                        #print("you are here you are here you are here minimizer")
                        self.num_times_wrong += 1
                        evaluation, first_move = self.pvs(next_state, max_depth - 1, False, alpha , beta)
                        value = min(value, evaluation)
                        beta = min(beta, evaluation)
                        re_search = True
                    else:
                        return value, first_move
            
                if beta <= alpha:
                    break
                ind += 1
            return value, first_move

        if not is_player_minimizer:
            value = -math.inf
            ind = 0
            re_search = False
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
                if ind == 0 or re_search:
                    evaluation, moves_to_here = self.pvs(next_state, max_depth - 1, True, alpha, beta)
                    value = max(value, evaluation)
                    alpha = max(alpha, evaluation)
                else:
                    evaluation, moves_to_here = self.pvs(next_state, max_depth - 1, True, alpha, beta)
                    # value = max(value, evaluation)
                    # print("value", evaluation)
                    # print("Alpha", alpha)
                    if alpha < evaluation :
                        #print("you are here max you are here max")
                        evaluation, moves_to_here = self.pvs(next_state, max_depth - 1, True, alpha, beta)
                        value = max(value, evaluation)
                        alpha = max(alpha, evaluation)
                        re_search = True
                    else:
                        return value, best_move
                if max(value, evaluation) is evaluation:
                    value = evaluation 
                    best_move = moves_to_here

                alpha = max(alpha, evaluation)
                ind += 1
                if beta <= alpha:
                    break
                
            return value, best_move