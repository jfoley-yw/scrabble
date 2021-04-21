import random
import string
import math
import torch
import torch.nn.functional as F
from collections import namedtuple

# code inspired by https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward', 'action_mask'))

class DQNScrabbleHelpers:
    @staticmethod
    def select_training_action(observation, epsilon_start, epsilon_end, epsilon_decay, step, model):
        sample = random.random()
        eps_threshold = epsilon_end + (epsilon_start - epsilon_end) * \
            math.exp(-1. * step / epsilon_decay)
        state_vector = DQNScrabbleHelpers.get_state_vector(observation.state)
        if sample > eps_threshold:
            with torch.no_grad():
                q_values = model(state_vector).detach()
                action_mask = torch.tensor([observation.action_mask], dtype = torch.float)
                masked_q_values = q_values + action_mask
            return masked_q_values.max(1).indices.item()
        else:
            return random.choice(observation.actions)

    @staticmethod
    def get_state_vector(state):
        board = state
        board_dimension = board.size
        # 27 = 26 letters in the alphabet + 1 character for empty space
        state = [0] * (board_dimension * board_dimension * 27)
        offset = 0
        for i in range(board_dimension):
            for j in range(board_dimension):
                tile = board.square(i, j).tile
                position = 26
                if tile != None:
                    position = string.ascii_lowercase.index(tile.lower())
                state[(offset * 27) + position] = 1
                offset += 1
        return torch.tensor([state], dtype = torch.float)

    @staticmethod
    def calculate_input_size(board_dimension):
        # one vector of length 27 per cell on the board + encoding of action
        # 27 = 26 letters in the alphabet + 1 character for empty space
        return (board_dimension * board_dimension * 27)

    @staticmethod
    def optimize_model(policy_net, target_net, memory, gamma, batch_size, optimizer):
        if len(memory) < batch_size:
            return

        transitions = memory.sample(batch_size)
        batch = Transition(*zip(*transitions))

        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                                batch.next_state)), dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])
        non_final_action_masks = torch.cat([batch.action_mask[i] for i in range(batch_size) if batch.next_state[i] is not None])

        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        state_action_values = policy_net(state_batch).gather(1, action_batch)

        target_net_output = target_net(non_final_next_states).detach()
        masked_target_net_output = target_net_output + non_final_action_masks
        next_state_values = torch.zeros(batch_size)
        next_state_values[non_final_mask] = masked_target_net_output.max(1)[0]

        # Compute the expected Q values
        expected_state_action_values = (next_state_values * gamma) + reward_batch

        # compute Huber loss
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values)

        # perform backpropogation / update policy network weights
        optimizer.zero_grad()
        loss.backward()
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
