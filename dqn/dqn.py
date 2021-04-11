import torch.nn as nn
import torch.nn.functional as F

# inspired by https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
class DQN(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(DQN, self).__init__()
        self.hidden_layer = nn.Linear(input_size, hidden_size)
        self.output_layer = nn.Linear(hidden_size, 1)

    def forward(self, x):
        x = self.hidden_layer(x)
        x = F.relu(x)
        return self.output_layer(x)
