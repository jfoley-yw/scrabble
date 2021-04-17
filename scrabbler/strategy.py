import random

class Strategy:
    '''
    Class representing a player's Strategy. The three algorithms should be a 
    subclass of this class and override the method choose move.
    '''
    def choose_move(self, game, rack, score_diff, opponents_rack, dictionary):
        raise Exception('Method not defined!')

class BaselineStrategy(Strategy):
    def choose_move(self, game, rack, score_diff, opponents_rack, dictionary):
        """ method that chooses a move based on this strategy"""

        # return the valid move with the highest score
        valid_moves = game.find_valid_moves(rack)
        if len(valid_moves) == 0:
            return None
        return valid_moves[0]

class RandomStrategy(Strategy):
    """ Strategy Class that chooses a random move instead of the move resulting in the highest score """
    def choose_move(self, game, rack, score_diff, opponents_rack, dictionary):
        # return the valid move with the highest score
        valid_moves = game.find_valid_moves(rack)
        rand = random.randint(0,len(valid_moves))
        if len(valid_moves) == 0:
            return None
        return valid_moves[rand]
