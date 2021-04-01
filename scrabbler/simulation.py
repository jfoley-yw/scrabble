from scrabbler.scrabbler import Game
import random
import time

class Simulation:
    LETTERS = ("AAAAAAAAAB"
               "BCCDDDDEEE"
               "EEEEEEEEEF"
               "FGGGHHIIII"
               "IIIIIJKLLL"
               "LMMNNNNNNO"
               "OOOOOOOPPQ"
               "RRRRRRSSSS"
               "TTTTTTUUUU"
               "VVWWXYYZ??")
    
    RACK_SIZE = 7

    @staticmethod
    def simulate_game():
        Simulation().simulate()

    def __init__(self):
        # Initialize game and board
        self.game = Game()
        self.board = self.game.board
        # Rack starts out empty.
        self.racks = [[], []]
        self.scores = [0, 0]
        # List of letters we can still pick from.
        self.bag = list(Simulation.LETTERS)
        self.player = 0
        self.endgame = False
        self.times = []

    def simulate(self):
        # Keep playing until we're out of tiles or solutions.
        while self.exectute_turn():
            # switch whose turn it is
            self.player = 1 - self.player
            # Show the game board. We could have also done print(board) here.
            self.game.show()

        self.print_end_game_message()

    def exectute_turn(self):
        self.generate_new_rack()

        # End game once either player has no letters left
        if not self.racks[self.player]:
            return False

        best_move = self.find_best_move()

        # If a valid move exists, then make best move, otherwise end game
        if best_move:
            self.make_move(best_move)
            return True
        else:
            return False

    def generate_new_rack(self):
        print("########################## Player %d turn ############################"%(self.player + 1))
        print("Bag: %s" % "".join(self.bag))
        print("Player %d rack pre-draw: %s" % (self.player + 1, self.racks[self.player]))
        self.generate_rack_and_bag()
        print("Player %d rack post-draw: %s" % (self.player + 1, self.racks[self.player]))

    def generate_rack_and_bag(self):
        """Randomly chooses tiles from bag and places in rack"""
        for i in range(Simulation.RACK_SIZE - len(self.racks[self.player])):
            # If bag has ended then end game begins (as of right now this 
            # doesn't formally mean anything, just print statement)
            if not self.bag:
                if not self.endgame:
                    print('|||||||||||||||||||| END GAME STARTS NOW ||||||||||||||||||||')
                    self.endgame = True
                break

            new_tile = random.choice(self.bag)
            self.racks[self.player].append(new_tile)
            self.bag.remove(new_tile)

    def find_best_move(self):
        # This function simply finds all valid moves and returns them ordered by score. The second parameter, which
        # is unused right now, used to limit the number of moves it returned, but I changed it so that all moves are
        # returned
        before = time.time()
        best_moves = self.game.find_valid_moves(''.join(self.racks[self.player]))
        self.times.append(time.time() - before)
        if len(best_moves) == 0:
            return None
        return best_moves[0]

    def make_move(self, move):
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
                    self.remove_tile_from_rack(move, i - start_column)
        else:
            for i in range(start_row, start_row + len(move.word)):
                if self.board.square(i, start_column).tile is None:
                    self.remove_tile_from_rack(move, i - start_row)

        # Actually play the move here
        self.game.play(move.start_square, move.word, move.direction)
        print("Player %d plays: %s" % (self.player + 1, move.word))
        self.scores[self.player] += move.score

    def remove_tile_from_rack(self, move, index):
        # if letter is not in word then it must be because a ? was used to make letter
        if move.word[index] not in self.racks[self.player]:
            self.racks[self.player].remove('?')
        else:
            self.racks[self.player].remove(move.word[index])

    def print_end_game_message(self):
        print('\nGAME OVER!')
        print("PLAYER 1 SCORE: %d ...... PLAYER 2 SCORE: %d" % (self.scores[0], self.scores[1]))
        print('Average move-generation time:', sum(self.times) / len(self.times))
