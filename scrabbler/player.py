import copy

class Player:
    '''
    Player Class represents a player in scrabble that takes in a midgame strategy and an optional endgame strategy. 
    '''
    def __init__ (self, midgame_strategy, endgame_strategy=None, name=None):
        self.mid_strat = midgame_strategy
        # If no end game strategy is specified, the midgame strategy will be applied as the endgame.
        if endgame_strategy is None:
            self.end_strat = midgame_strategy
        else:
            self.end_strat = endgame_strategy

        # initialize score and rack
        self.score = 0
        self.rack = []

        self.name = name # might be useful for plotting during analysis
        self.endgame_score = None

        self.LETTER_VALUE = {"A": 1, "B":4, "C":4, "D":2, "E":1, "F":4, "G":3, "H":3, "I":1, "J":10, "K":5, "L":2, 
            "M":4, "N":2, "O":1, "P":4, "Q":10, "R":1, "S":1, "T":1, "U":2, "V":5, "W":4, "X":8, "Y":3, "Z":10}

    def choose_move(self, is_endgame, game, other_score, other_rack, dictionary):
        # chooses a move for the player based on the endgame and midgame strategies
        score_diff = self.score - other_score
        if is_endgame:
            print("END GAME STRATEGY ACITVATED")
            return self.end_strat.choose_move(game, self.rack, score_diff, other_rack, dictionary)
        else:
            return self.mid_strat.choose_move(game, self.rack, score_diff, other_rack, dictionary)

    def is_rack_empty(self):
        return len(self.rack) == 0 

    def get_rack(self):
        """getter for the player's rack"""
        return self.rack   

    def update_rack(self, new_tiles):
        """adds new tiles to the player's rack given a list of new tiles"""
        self.rack += new_tiles

    def update_score(self, move_score):
        """updates a players score once they make a move
        Inputs: move_score (int) representing the score of the letters placed on the board"""
        self.score += move_score

    def remove_tile_from_rack(self, move, index):
        """ removes the tiles from the rack given a move and an index"""
        # if letter is not in word then it must be because a ? was used to make letter
        if move.word[index] not in self.rack:
            self.rack.remove('?')
        else:
            self.rack.remove(move.word[index])

    def get_score(self):
        """ getter for the player's score"""
        return self.score

    def set_endgame_score(self):
        self.endgame_score = copy.deepcopy(self.get_score())

    def score_tiles_in_rack(self):
        if len(self.rack) != 0:
            for tile in self.rack:
                self.score - (2*self.LETTER_VALUE[tile])
        return self.score

