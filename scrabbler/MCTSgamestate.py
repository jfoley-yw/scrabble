''' Represents a state of the game as well as a node in the state space so that
    it can be used as a key in dictionaries tracking rewards/visits
'''
class MCTSgamestate:
    def __init__(self, board_state, rack_state, is_my_turn, score_differential):
        # board_state is a tuple of size rows * columns where each entry is the tile on the board
        # or None if there is no tile.
        self.board_state = board_state

        # rack_state is a tuple of size 27 where each entry is number of corresponding letters
        # e.g. "ABBEF?" would be (1,2,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1)
        self.rack_state = rack_state

        # True if it's my turn, False otherwise
        self.is_my_turn = is_my_turn

        # my score minus other player's score
        self.score_differential = score_differential

    def __members(self):
        return self.board_state, self.rack_state, self.is_my_turn, self.score_differential

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def __hash__(self):
        return hash(self.__members())
