from scrabbler.player import Player

class DQNPlayer(Player):
    def __init__(self, midgame_strategy, endgame_strategy=None, name=None):
        super().__init__(midgame_strategy, endgame_strategy, name)
        self.score_one_turn_ago = None

    def update_score(self, move_score):
        self.score_one_turn_ago = self.score
        self.score += move_score

    def get_old_score(self):
        return self.score_one_turn_ago
