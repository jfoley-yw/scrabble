import scrabbler as sc
import random

LETTERS = """\
AAAAAAAAAB\
BCCDDDDEEE\
EEEEEEEEEF\
FGGGHHIIII\
IIIIIJKLLL\
LMMNNNNNNO\
OOOOOOOPPQ\
RRRRRRSSSS\
TTTTTTUUUU\
VVWWXYYZ??\
"""

ALREADY_ENDGAME = False

def get_full_bag():
    """Returns a list of letters in the whole bag."""
    return list(LETTERS)


def generate_rack_and_bag(rack, bag):
    """Randomly chooses tiles from bag and places in rack"""
    for i in range(7 - len(rack)):
        # If bag has ended then end game begins (as of right now this 
        # doesn't formally mean anything, just print statement)
        if not bag:
            global ALREADY_ENDGAME
            if not ALREADY_ENDGAME:
                print('|||||||||||||||||||| END GAME STARTS NOW ||||||||||||||||||||')
                ALREADY_ENDGAME = True
            return rack, bag
        new_tile = random.choice(bag)
        rack.append(new_tile)
        bag.remove(new_tile)

    return rack, bag


def main():
    # List of letters we can still pick from.
    bag = get_full_bag()

    # Rack starts out empty.
    player1Turn = True
    player1Rack = []
    player2Rack = []
    player1Score = 0
    player2Score = 0

    # Initialize game and board
    game = sc.Game()
    board = game.get_board()

    # Keep playing until we're out of tiles or solutions.
    while True:
        if player1Turn:
            print("########################## Player 1 turn ############################")
            print("Bag: %s" % "".join(bag))
            print("Player 1 rack pre-draw:", player1Rack)
            player1Rack, bag = generate_rack_and_bag(player1Rack, bag)
            print("Player 1 rack post-draw:", player1Rack)

            # End game once either player has no letters left
            if not player1Rack:
                break

            # This function simply finds all valid moves and returns them ordered by score. The second parameter, which
            # is unused right now, used to limit the number of moves it returned, but I changed it so that all moves are
            # returned
            best_move = game.find_best_moves(''.join(player1Rack))

            # If a valid move exists, then make best move, otherwise end game
            if best_move:
                best_move = best_move[0]
                start_row = best_move.start_square[0]
                start_column = best_move.start_square[1]

                # Remove tiles that are about to be played from rack. Look at the squares on board that
                # will contain word after tiles are placed. If square has no tile (no letter there so
                # this move must place a letter there) then we must remove the letter from the rack that 
                # corresponds to the letter that will be placed (based on index in word). If the square has
                # no letter AND the letter that will be placed is not in the rack then that means that it
                # must be a ? tile so remove the ? from the rack.
                if best_move.direction == "across":
                    for i in range(start_column, start_column + len(best_move.word)):
                        if board.square(start_row, i).get_tile() is None:

                            # if letter is not in word then it must be because a ? was used to make letter
                            if best_move.word[i - start_column] not in player1Rack:
                                player1Rack.remove('?')
                            else:
                                player1Rack.remove(best_move.word[i - start_column])
                else:
                    for i in range(start_row, start_row + len(best_move.word)):
                        if board.square(i, start_column).get_tile() is None:

                            # if letter is not in word then it must be because a ? was used to make letter
                            if best_move.word[i - start_row] not in player1Rack:
                                player1Rack.remove('?')
                            else:
                                player1Rack.remove(best_move.word[i - start_row])

                # Actually play the move here
                game.play(best_move.start_square, best_move.word, best_move.direction)
                print("Player 1 plays: %s" % best_move.word)
                player1Score += best_move.score
            else:
                break

        else:
            print("########################## Player 2 turn ############################")
            print("Bag: %s" % "".join(bag))
            print("Player 2 rack pre-draw:", player2Rack)
            player2Rack, bag = generate_rack_and_bag(player2Rack, bag)
            print("Player 2 rack post-draw:", player2Rack)

            # End game once either player has no letters left
            if not player2Rack:
                break

            # This function simply finds all valid moves and returns them ordered by score. The second parameter, which
            # is unused right now, used to limit the number of moves it returned, but I changed it so that all moves are
            # returned
            best_move = game.find_best_moves(''.join(player2Rack))

            # If a valid move exists, then make best move, otherwise end game
            if best_move:
                best_move = best_move[0]
                start_row = best_move.start_square[0]
                start_column = best_move.start_square[1]

                # Remove tiles that are about to be played from rack. Look at the squares on board that
                # will contain word after tiles are placed. If square has no tile (no letter there so
                # this move must place a letter there) then we must remove the letter from the rack that 
                # corresponds to the letter that will be placed (based on index in word). If the square has
                # no letter AND the letter that will be placed is not in the rack then that means that it
                # must be a ? tile so remove the ? from the rack.
                if best_move.direction == "across":
                    for i in range(start_column, start_column + len(best_move.word)):
                        if board.square(start_row, i).get_tile() is None:

                            # if letter is not in word then it must be because a ? was used to make letter
                            if best_move.word[i - start_column] not in player2Rack:
                                player2Rack.remove('?')
                            else:
                                player2Rack.remove(best_move.word[i - start_column])
                else:
                    for i in range(start_row, start_row + len(best_move.word)):
                        if board.square(i, start_column).get_tile() is None:

                            # if letter is not in word then it must be because a ? was used to make letter
                            if best_move.word[i - start_row] not in player2Rack:
                                player2Rack.remove('?')
                            else:
                                player2Rack.remove(best_move.word[i - start_row])

                # Actually play the move here 
                game.play(best_move.start_square, best_move.word, best_move.direction)
                print("Player 2 plays: %s" % best_move.word)
                player2Score += best_move.score

            else:
                break

        # switch whose turn it is
        player1Turn = not player1Turn

        # Show the game board. We could have also done print(board) here.
        game.show()

    print('\nGAME OVER!')
    print("PLAYER 1 SCORE: %d ...... PLAYER 2 SCORE: %d" % (player1Score, player2Score))


if __name__ == "__main__":
    main()
