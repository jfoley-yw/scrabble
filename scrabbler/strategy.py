class Strategy:
    '''
    Class representing a player's Strategy. The three algorithms should be a 
    subclass of this class and override the method choose move.
    '''
    def choose_move(self, game, rack):
        raise Exception('Method not defined!')

class BaselineStrategy(Strategy):
    def choose_move(self, game, rack):
        """ method that chooses the best move"""

        # return the valid move with the highest score
        valid_moves = game.find_valid_moves(rack)
        if len(valid_moves) == 0:
            return None
        return valid_moves[0]
