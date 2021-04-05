
class Strategy:
    '''
    Class representing a player's Strategy. The three algorithms should be a 
    subclass of this class and override the method choose move.
    '''
    def choose_move(self, game, rack):
        """ method that chooses the best move"""

        # return the valid move with the highest score
        return game.find_valid_moves(rack)[0]