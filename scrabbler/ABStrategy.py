from scrabbler.ABgamestate import ABGamestate
from scrabbler.strategy import Strategy
import copy
import math
from collections import defaultdict



class ABStrategy(Strategy):
    def __init__(self):
        self.dictionary = None

    def choose_move(self, game, rack, score_diff, opponent_rack, dictionary):
        self.dictionary = dictionary
        board = copy.deepcopy(game.board)
        gamestate = ABGamestate(board, rack, opponent_rack, 0, score_diff, [])
        value, move = self.minimax(gamestate, 14, False, -math.inf, math.inf)
        print("move", move)
        return move
        
    def minimax(self, cur_state, max_depth, is_player_minimizer, alpha, beta):
        best_move = None
        print("CURRENT DEPTH", max_depth)

        if max_depth == 0 or cur_state.is_end_state():
            print("Leaf", cur_state.score_diff)
            return cur_state.score_diff, cur_state.moves[0]
        
        print("Not a leaf")
        moves = cur_state.find_next_moves(self.dictionary)
        
        if is_player_minimizer:
            print("Minimizer")
            value = math.inf
            for move in moves:
                print("Minimizer Move", move)

                # get the next rack for the minimizing player
                next_rack = cur_state.get_next_rack(move)

                # update the board with the new move
                next_board = cur_state.get_next_board(move, self.dictionary)

                # update the score diff
                next_score_diff = cur_state.new_score_diff(move.score)
                print("Next score Diff minimixer", next_score_diff)

                # update the moves to get to the gamestate
                moves_to_get_here = cur_state.update_moves(move)

                # create the next state
                next_state = ABGamestate(next_board, cur_state.player_rack, next_rack, is_player_minimizer=False, score_diff=next_score_diff, moves=moves_to_get_here)

                evaluation, first_move = self.minimax(next_state, max_depth - 1, False, alpha , beta)
                print("Depth after eval max", max_depth)
                value = min(value, evaluation)
                print("Minumum", value)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    print("Minimizer Break")
                    break
            print("Val Minimizer", value)
            return value, first_move

        if not is_player_minimizer:
            value = -math.inf
            for move in moves:
                print("Maximizer")
                print("Maximizer move", move)
                # get the next rack for the minimizing player
                next_rack = cur_state.get_next_rack(move)

                # update the board with the new move
                next_board = cur_state.get_next_board(move, self.dictionary)
                # update the score diff
                next_score_diff = cur_state.new_score_diff(move.score)
                print("next score diff maximizer", next_score_diff)
                # update the moves to get to the gamestate
                moves_to_get_here = cur_state.update_moves(move)

                # create the next state
                next_state = ABGamestate(next_board, next_rack, cur_state.opponent_rack, is_player_minimizer=True, score_diff=next_score_diff, moves=moves_to_get_here)
                evaluation, moves_to_here = self.minimax(next_state, max_depth - 1, True, alpha, beta)
                print("Depth after eval max", max_depth)
                value = max(value, evaluation)
                if max(value, evaluation) is evaluation:
                    value = evaluation 
                    best_move = moves_to_here
                print("maximum", value)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    print("max break")
                    break
                
            print("Val Maximizer", value)
            return value, best_move