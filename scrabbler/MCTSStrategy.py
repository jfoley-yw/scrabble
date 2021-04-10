import copy
import random
import math

from scrabbler.strategy import Strategy
from collections import defaultdict
from scrabbler.gameState import GameState


''' Node must be represented by a state of the board/rack/bag-size. dict with those three props
should be used as key for a dict from game state -> reward / attempts'''
class MCTSStrategy(Strategy):
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

    def __init__(self, num_rollouts = 5, time_limit = 300, exploration_weight=1):
        self.num_rollouts = num_rollouts
        self.time_limit = time_limit  # in seconds # TODO - how to incorporate a time limit
        self.reward_dict = defaultdict(int)
        self.visits_dict = defaultdict(int)
        self.next_states = {}
        self.dictionary = None
        self.exploration_weight = exploration_weight
        self.tiles = {'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1,
                         'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
                         'Y': 4, 'Z': 10}
        # self.state_to_score_differential = defaultdict(int)
        # self.state_to_potential_bag = defaultdict(set)
        self.move_between_states = {}

    def add_dictionary(self, dictionary):
        self.dictionary = dictionary

    def choose_move(self, game, rack, current_score_differential, is_player1):
        # self.game = copy.copy(game) # do i need a copy of this?
        tupled_board = tuple(square.tile for square in game.board.get_board())
        tupled_rack = self.tuplify_rack(rack)
        current_game_state = GameState(tupled_board, tupled_rack, is_player1, current_score_differential)
        # self.state_to_score_differential[current_game_state] = current_score_differential
        self.board = copy.deepcopy(game.board)
        self.original_board = copy.deepcopy(game.board)  # change both board and original board as we go down to selected node and then update board all the way down to end, and then backprogate and reset board to original
        # self.rack = rack
        # self.rack = copy.deepcopy(rack)
        # self.original_rack = copy.deepcopy(rack)
        # self.bag = self.deduce_potential_bag(tupled_board, tupled_rack)  # TODO - we can generate bag when we start simulation. no need to track during selection
        # self.original_bag = copy.copy(self.bag)
        # self.state_to_potential_bag[current_game_state] = self.original_bag
        # self.game.board = copy.deepcopy(game.board)
        print('Starting Rollouts')
        for i in range(self.num_rollouts):
            self.rollout(current_game_state)
        best_move = self.get_best_move(current_game_state)
        return best_move

    def deduce_potential_bag(self, tupled_board, tupled_rack):
        starting_letters = list(MCTSStrategy.LETTERS)
        curr_rack = self.untuplify_rack(tupled_rack)
        for i in range(len(tupled_board)):
            letter = tupled_board[i]
            if letter:
                try:
                    starting_letters.remove(letter)
                except:
                    for j in range(self.board.size):
                        print(tupled_board[j*self.board.size:j*self.board.size+self.board.size])
                    print('The letter: ', letter)
                    raise ValueError
        for i in range(len(curr_rack)):
            starting_letters.remove(curr_rack[i])

        return starting_letters

    def get_best_move(self, game_state):
        if self.is_terminal(game_state):
            return None

        if game_state not in self.next_states:
            print('game_state was not in self.next_states')
            return None
            # return self.find_random_child(game_state)  # TODO - should be a move, not a state

        def score(state):
            if self.visits_dict[state] == 0:
                return float("-inf")  # avoid unseen moves
            return self.reward_dict[state] / self.visits_dict[state]  # average reward

        best_next_state = max(self.next_states[game_state], key=score)
        return self.move_between_states[(game_state, best_next_state)]
        # return max(self.next_states[game_state], key=score)

    def find_random_child(self, game_state):
        next_states = tuple(self.find_simulated_next_states(game_state))
        random_next_state = random.choice(next_states)
        requisite_move = self.move_between_states[(game_state, random_next_state)]
        # self.update_board_rack_with_move(self.board, requisite_move)
        return random_next_state

    def find_random_sim_child(self, game_state):
        next_states = tuple(self.find_simulated_next_states(game_state))
        random_next_state = random.choice(next_states)
        requisite_move = self.move_between_states[(game_state, random_next_state)]
        self.update_sim_board_with_move(self.board, requisite_move)

        return random_next_state

    def tuplify_rack(self, rack):
        char_count = defaultdict(int)
        for char in rack:
            char_count[char] += 1
        all_chars = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','?']
        rack_tuple = tuple(char_count[char] for char in all_chars)
        return rack_tuple

    def rollout(self, game_state):
        path = self.select(game_state)
        leaf = path[-1]
        self.expand(leaf)
        reward = self.simulate(leaf)
        self.backpropagate(path, reward)
        self.board = copy.deepcopy(self.original_board)

    def select(self, game_state):
        # select unexplored descendent of root node
        path = []
        while True:
            path.append(game_state)
            if game_state not in self.next_states or not self.next_states[game_state]:
                # node is either unexplored or terminal
                return path
            unexplored = self.next_states[game_state] - self.next_states.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            game_state = self.uct_select(game_state)  # descend a layer deeper

    def expand(self, game_state):
        if game_state in self.next_states:
            return  # already expanded

        self.next_states[game_state] = self.find_next_states(game_state)

    def simulate(self, game_state):
        "Returns the reward for a random simulation (to completion) of `node`"
        invert_reward = True
        while True:
            if self.is_terminal(game_state):
                score_differential = game_state.score_differential  # TODO - don't want to mix game tree and sim tree, should i have findrandomchild return score so it's contained to just this sim and not saved
                # TODO - Or maybe just dont add game state to the game tree structure even though i am creating the game_state objects as we sim
                if score_differential > 0:
                    reward = 1
                elif score_differential < 0:
                    reward = 0
                else:
                    reward = 0.5
                if invert_reward:
                    return 1 - reward
                return reward

            game_state = self.find_random_sim_child(game_state)
            invert_reward = not invert_reward

    def backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for game_state in reversed(path):
            self.visits_dict[game_state] += 1
            self.reward_dict[game_state] += reward
            reward = 1 - reward

    def uct_select(self, game_state):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expanded:
        assert all(n in self.next_states for n in self.next_states[game_state])

        log_N_vertex = math.log(self.visits_dict[game_state])

        def uct(n):
            "Upper confidence bound for trees"
            return self.reward_dict[n] / self.visits_dict[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.visits_dict[n]
            )
        next_game_state = max(self.next_states[game_state], key=uct)
        requisite_move = self.move_between_states[(game_state, next_game_state)]
        self.update_board_with_move(self.board, requisite_move)  #, self.rack)
        return next_game_state

    def update_board_with_move(self, current_board, move):  #, rack):  # TODO - probably should just copy.copy board after select instead of updating both
        start_square = move.start_square
        # start_row = start_square[0]
        # start_column = start_square[1]
        word = move.word
        direction = move.direction

        # if move.direction == "across":
        #     for i in range(start_column, start_column + len(move.word)):
        #         if current_board.square(start_row, i).tile is None:
        #             if move.word[i - start_column] not in self.rack:
        #                 rack.remove('?')
        #             else:
        #                 rack.remove(move.word[i - start_column])
        # else:
        #     for i in range(start_row, start_row + len(move.word)):
        #         if current_board.square(i, start_column).tile is None:
        #             if move.word[i - start_row] not in self.rack:
        #                 rack.remove('?')
        #             else:
        #                 rack.remove(move.word[i - start_row])

        print('current board')
        print(current_board)
        current_board.place_word(start_square, word, direction)
        print(current_board)

        # update affected cross sets
        current_board.update_cross_set(start_square, direction, self.dictionary)
        other_direction = "across" if direction == "down" else "down"
        coordinate = start_square
        for _ in word:
            current_board.update_cross_set(coordinate, other_direction, self.dictionary)
            coordinate = current_board.offset(coordinate, direction, 1)

    def find_next_states(self, game_state):  # move generator
        mid = int(self.board.size / 2)
        curr_rack = self.untuplify_rack(game_state.rack_state)

        if self.board.empty:
            moves = self.board.generate_moves((mid, mid), "across", curr_rack, self.dictionary, self.tiles, {})
        else:
            across_moves = self.board.find_best_moves(curr_rack, "across", self.dictionary, self.tiles)
            down_moves = self.board.find_best_moves(curr_rack, "down", self.dictionary, self.tiles)
            moves = across_moves + down_moves

        # TODO - maybe I only do some of the moves based on highest score so that algo runs faster
        # moves.sort(key=lambda move_: move_.score, reverse=True)

        next_states = set()

        # TODO - maybe I only do some of the moves based on highest score so that algo runs faster
        for move in moves:
            next_board = [square.tile for square in self.board.get_board()]
            index = move.start_square[0] * self.board.size + move.start_square[1]
            for i in range(len(move.word)):
                if move.direction == "across":
                    next_board[index + i] = move.word[i]
                else:
                    next_board[index + i * self.board.size] = move.word[i]
            tupled_board = tuple(next_board)

            # start_row = move.start_square[0]
            # start_column = move.start_square[1]
            # next_rack = copy.deepcopy(curr_rack)
            # if move.direction == "across":
            #     for i in range(start_column, start_column + len(move.word)):
            #         if self.board.square(start_row, i).tile is None:
            #             if move.word[i - start_column] not in next_rack:
            #                 next_rack.remove('?')
            #             else:
            #                 next_rack.remove(move.word[i - start_column])
            # else:
            #     for i in range(start_row, start_row + len(move.word)):
            #         if self.board.square(i, start_column).tile is None:
            #             if move.word[i - start_row] not in next_rack:
            #                 next_rack.remove('?')
            #             else:
            #                 next_rack.remove(move.word[i - start_row])

            curr_bag = self.deduce_potential_bag(tupled_board, (
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # TODO - maybe have excluded tiles so next player cant get current players tiles
            next_rack = []
            for i in range(7):
                if len(curr_bag) > 0:
                    new_letter = random.choice(curr_bag)
                    next_rack.append(new_letter)
                    curr_bag.remove(new_letter)
                else:
                    break

            # TODO - Have to add letters from bag to next rack
            # curr_bag = self.deduce_potential_bag(tupled_board, self.tuplify_rack(next_rack))
            # for i in range(7 - len(next_rack)):
            #     if len(curr_bag) > 0:
            #         next_rack.append(random.choice(curr_bag))
            #     else:
            #         break

            tupled_rack = self.tuplify_rack(next_rack)
            if not game_state.is_player1_turn:
                next_game_state = GameState(tupled_board, tupled_rack, not game_state.is_player1_turn, game_state.score_differential + move.score)
            else:
                next_game_state = GameState(tupled_board, tupled_rack, not game_state.is_player1_turn, game_state.score_differential - move.score)

            next_states.add(next_game_state)

            self.move_between_states[(game_state, next_game_state)] = move
        return next_states

    def find_simulated_next_states(self, game_state):  # move generator
        mid = int(self.board.size / 2)
        curr_rack = self.untuplify_rack(game_state.rack_state)

        if self.board.empty:
            moves = self.board.generate_moves((mid, mid), "across", curr_rack, self.dictionary, self.tiles, {})
        else:
            across_moves = self.board.find_best_moves(curr_rack, "across", self.dictionary, self.tiles)
            down_moves = self.board.find_best_moves(curr_rack, "down", self.dictionary, self.tiles)
            moves = across_moves + down_moves

        # TODO - maybe I only do some of the moves based on highest score so that algo runs faster
        # moves.sort(key=lambda move_: move_.score, reverse=True)

        next_states = set()

        # TODO - maybe I only do some of the moves based on highest score so that algo runs faster
        for move in moves:
            next_board = [square.tile for square in self.board.get_board()]
            index = move.start_square[0] * self.board.size + move.start_square[1]
            for i in range(len(move.word)):
                if move.direction == "across":
                    next_board[index + i] = move.word[i]
                else:
                    next_board[index + i * self.board.size] = move.word[i]
            tupled_board = tuple(next_board)

            # start_row = move.start_square[0]
            # start_column = move.start_square[1]
            # next_rack = copy.deepcopy(curr_rack)
            # if move.direction == "across":
            #     for i in range(start_column, start_column + len(move.word)):
            #         if self.board.square(start_row, i).tile is None:
            #             if move.word[i - start_column] not in next_rack:
            #                 next_rack.remove('?')
            #             else:
            #                 next_rack.remove(move.word[i - start_column])
            # else:
            #     for i in range(start_row, start_row + len(move.word)):
            #         if self.board.square(i, start_column).tile is None:
            #             if move.word[i - start_row] not in next_rack:
            #                 next_rack.remove('?')
            #             else:
            #                 next_rack.remove(move.word[i - start_row])

            curr_bag = self.deduce_potential_bag(tupled_board, (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))
            next_rack = []
            for i in range(7):
                if len(curr_bag) > 0:
                    new_letter = random.choice(curr_bag)
                    next_rack.append(new_letter)
                    curr_bag.remove(new_letter)
                else:
                    break

            # TODO - Here and in find_next_states, have to add letters from bag to next rack
            # curr_bag = self.deduce_potential_bag(tupled_board, self.tuplify_rack(next_rack))
            # for i in range(7 - len(next_rack)):
            #     if len(curr_bag) > 0:
            #         next_rack.append(random.choice(curr_bag))
            #     else:
            #         break

            tupled_rack = self.tuplify_rack(next_rack)
            if not game_state.is_player1_turn:
                next_game_state = GameState(tupled_board, tupled_rack, not game_state.is_player1_turn,
                                            game_state.score_differential + move.score)
            else:
                next_game_state = GameState(tupled_board, tupled_rack, not game_state.is_player1_turn,
                                            game_state.score_differential - move.score)

            next_states.add(next_game_state)

            self.move_between_states[(game_state, next_game_state)] = move
        return next_states

    def is_terminal(self, game_state):
        # check to see if there are no valid moves
        if game_state.rack_state == (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) \
                or not self.has_potential_next_states(game_state):
            return True
        return False

    def has_potential_next_states(self, game_state):  # move generator # TODO - used in simulation so needs to make sure self.board is updated. Change self.rack to be game_state's rack
        mid = int(self.board.size / 2)

        # if self.board.empty:
        #     moves = self.board.generate_moves((mid, mid), "across", self.rack, self.dictionary, self.tiles, {})
        # else:
        #     across_moves = self.board.find_best_moves(self.rack, "across", self.dictionary, self.tiles)
        #     down_moves = self.board.find_best_moves(self.rack, "down", self.dictionary, self.tiles)
        #     moves = across_moves + down_moves

        curr_rack = self.untuplify_rack(game_state.rack_state)

        if self.board.empty:
            moves = self.board.generate_moves((mid, mid), "across", curr_rack, self.dictionary, self.tiles, {})
        else:
            across_moves = self.board.find_best_moves(curr_rack, "across", self.dictionary, self.tiles)
            down_moves = self.board.find_best_moves(curr_rack, "down", self.dictionary, self.tiles)
            moves = across_moves + down_moves

        if len(moves) > 0:
            return True
        return False

    def update_sim_board_with_move(self, current_board, move):  # TODO - probably should just copy.copy board after select instead of updating both
        start_square = move.start_square
        start_row = start_square[0]
        start_column = start_square[1]
        word = move.word
        direction = move.direction

        # if move.direction == "across":
        #     for i in range(start_column, start_column + len(move.word)):
        #         if current_board.square(start_row, i).tile is None:
        #             if move.word[i - start_column] not in self.rack:
        #                 rack.remove('?')
        #             else:
        #                 rack.remove(move.word[i - start_column])
        # else:
        #     for i in range(start_row, start_row + len(move.word)):
        #         if current_board.square(i, start_column).tile is None:
        #             if move.word[i - start_row] not in self.rack:
        #                 rack.remove('?')
        #             else:
        #                 rack.remove(move.word[i - start_row])

        current_board.place_word(start_square, word, direction)

        # update affected cross sets
        current_board.update_cross_set(start_square, direction, self.dictionary)
        other_direction = "across" if direction == "down" else "down"
        coordinate = start_square
        for _ in word:
            current_board.update_cross_set(coordinate, other_direction, self.dictionary)
            coordinate = current_board.offset(coordinate, direction, 1)

    def untuplify_rack(self, rack_state):
        rack = []
        for i in range(len(rack_state)):
            for j in range(rack_state[i]):
                if i == len(rack_state) - 1:  # question mark
                    rack.append("?")
                else:
                    rack.append(chr(65 + i))

        return rack
