import random

from scrabbler.strategy import Strategy

class RandomStrategy(Strategy):
    def choose_move(self, game, rack, current_score_differential, other_rack, dictionary):
        moves = game.find_valid_moves(rack)
        if moves:
            return random.choice(moves)
        return None