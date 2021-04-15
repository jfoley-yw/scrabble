import random
import string
import torch
import torch.nn.functional as F
from collections import namedtuple

# code inspired by https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward', 'next_actions'))

class DQNHelpers:
    @staticmethod
    def get_state_vector(game):
        board_dimension = game.board.size
        # 27 = 26 letters in the alphabet + 1 character for empty space
        state = [0] * (board_dimension * board_dimension * 27)
        offset = 0
        for i in range(board_dimension):
            for j in range(board_dimension):
                tile = game.board.square(i, j).tile
                position = 26
                if tile != None:
                    position = string.ascii_lowercase.index(tile.lower())
                state[(offset * 27) + position] = 1
                offset += 1
        return torch.tensor([state], dtype = torch.float)

    @staticmethod
    def get_action_vector(word):
        action = [0] * 26
        for i in range(len(word)):
            position = string.ascii_lowercase.index(word[i].lower())
            action[position] += 1
        return torch.tensor([action], dtype = torch.float)

    @staticmethod
    def get_input_vector(game, word):
        return torch.cat((DQNHelpers.get_state_vector(game), DQNHelpers.get_action_vector(word)), 1)

    @staticmethod
    def calculate_input_size(board_dimension):
        # one vector of length 27 per cell on the board + encoding of action
        # 27 = 26 letters in the alphabet + 1 character for empty space
        return (board_dimension * board_dimension * 27) + 26

    @staticmethod
    def optimize_model(policy_net, target_net, memory, gamma, batch_size, optimizer):
        if len(memory) < batch_size:
            return

        transitions = memory.sample(batch_size)
        batch = Transition(*zip(*transitions))

        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        state_action_batch = torch.cat((state_batch, action_batch), 1)
        state_action_values = policy_net(state_action_batch)

        # calculate max[Q(s', a)] for each s' in the batch
        next_state_values = [float('-inf')] * batch_size
        for i_batch in range(batch_size):
            next_state = batch.next_state[i_batch]
            if next_state == None:
                next_state_values[i_batch] = 0
                continue
            next_actions = batch.next_actions[i_batch]
            for next_action in next_actions:
                input_vector = torch.cat((next_state, next_action), 1)
                next_state_values[i_batch] = max(next_state_values[i_batch], target_net(input_vector).item())

        next_state_values = torch.tensor([next_state_values]).swapaxes(0, 1)
        expected_state_action_values = (next_state_values * gamma) + reward_batch

        # compute Huber loss
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values)

        # perform backpropogation / update policy network weights
        optimizer.zero_grad()
        loss.backward()
        for param in policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        optimizer.step()

        return loss.item()

class ReplayMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)
