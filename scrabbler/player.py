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

    def choose_move(self, is_endgame, game):
        # chooses a move for the player based on the endgame and midgame strategies
        if is_endgame:
            return self.end_strat.choose_move(game, self.rack)
        else:
            return self.mid_strat.choose_move(game, self.rack)
        

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



    