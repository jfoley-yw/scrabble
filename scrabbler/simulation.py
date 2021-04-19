from scrabbler.scrabbler import Game
import random
import copy

class Simulation:
    # LETTERS = ("AAAAAAAAAB"
    #            "BCCDDDDEEE"
    #            "EEEEEEEEEF"
    #            "FGGGHHIIII"
    #            "IIIIIJKLLL"
    #            "LMMNNNNNNO"
    #            "OOOOOOOPPQ"
    #            "RRRRRRSSSS"
    #            "TTTTTTUUUU"
    #            "VVWWXYYZ")  # TODO - deleted the question marks to remove issue of deducing bag

    LETTERS = ("AAAB"
               "EEE"
               "EE"
               "FII"
               "IJKL"
               "LMO")
    
    RACK_SIZE = 4

    @staticmethod
    def simulate_game(player1, player2, start_player = None):
        return Simulation(player1, player2, start_player).simulate()

    def __init__(self, player1, player2, start_player = None):
        # Initialize game and board
        self.game = Game()
        self.board = self.game.board
        # List of letters we can still  pick from.
        self.bag = list(Simulation.LETTERS)
        self.players = (player1, player2)
        if start_player != None:
            self.player = start_player
        else:   
            # randomly choose which player goes first so that it varies during each simulation
            # self.player = random.randint(0,1)  # ANDREW - TODO
            self.player = 0
        self.endgame = False

        # fills the players racks to start the game
        self.generate_rack_and_bag(0)
        self.generate_rack_and_bag(1)

    def simulate(self):
        # Keep playing until we're out of tiles or solutions.
        while self.simulate_step():
            self.game.show()

        self.print_end_game_message()
       
        p1_score = self.players[1].get_score()
        p0_score = self.players[0].get_score()
        return p0_score, p1_score

    def simulate_step(self):
        done = self.exectute_turn()
        # switch whose turn it is
        self.player = 1 - self.player
        return done

    def exectute_turn(self):
        # End of the game once either player has no letters left
        if self.players[0].is_rack_empty() or self.players[1].is_rack_empty():
            return False

        print("########################## Player %d turn ############################"%(self.player + 1))
        print("Bag: %s" % "".join(self.bag))
        print("Player %d rack pre-draw: %s" % (self.player + 1, self.players[self.player].get_rack()))

        if self.player == 0:
            other_player = 1
        else:
            other_player = 0

        best_move = self.players[self.player].choose_move(self.endgame, self.game, self.players[other_player].get_score(), self.players[other_player].get_rack(), self.game.dictionary)

        # If a valid move exists, then make best move, otherwise end game
        if best_move:
            self.make_move(best_move)
            self.generate_new_rack()
            return True
        else:
            return False

    def generate_new_rack(self):
        """ Generates new rack after drawing tiles from the bag and prints out the new rack before and after the draw."""
        self.generate_rack_and_bag(self.player)
        print("Player %d rack post-draw: %s" % (self.player + 1, self.players[self.player].get_rack()))

    def generate_rack_and_bag(self, player):
        """Randomly chooses tiles from bag and places in rack"""
        new_letters = []
        for i in range(Simulation.RACK_SIZE - len(self.players[player].get_rack())):
            # If bag has ended then end game begins 
            if not self.bag:
                if not self.endgame:
                    print('|||||||||||||||||||| END GAME STARTS NOW ||||||||||||||||||||')
                    self.endgame = True
                    self.players[0].set_endgame_score()
                    self.players[1].set_endgame_score()
                break

            new_tile = random.choice(self.bag)
            new_letters.append(new_tile)
            self.bag.remove(new_tile)
        self.players[player].update_rack(new_letters)

    def make_move(self, move):
        """ Places given move on the board and removes tiles from the rack"""
        start_row = move.start_square[0]
        start_column = move.start_square[1]

        # Remove tiles that are about to be played from rack. Look at the squares on board that
        # will contain word after tiles are placed. If square has no tile (no letter there so
        # this move must place a letter there) then we must remove the letter from the rack that 
        # corresponds to the letter that will be placed (based on index in word). If the square has
        # no letter AND the letter that will be placed is not in the rack then that means that it
        # must be a ? tile so remove the ? from the rack.
        if move.direction == "across":
            for i in range(start_column, start_column + len(move.word)):
                if self.board.square(start_row, i).tile is None:
                    self.players[self.player].remove_tile_from_rack(move, i - start_column)
        else:
            for i in range(start_row, start_row + len(move.word)):
                if self.board.square(i, start_column).tile is None:
                    self.players[self.player].remove_tile_from_rack(move, i - start_row)

        # Actually play the move here
        self.game.play(move.start_square, move.word, move.direction)
        print("Player %d plays: %s" % (self.player + 1, move.word))
        self.players[self.player].update_score(move.score)

    def print_end_game_message(self):
        print("\nGAME OVER!")
        print("PLAYER 1 SCORE: %d ...... PLAYER 2 SCORE: %d" % (self.players[0].get_score(), self.players[1].get_score()))
