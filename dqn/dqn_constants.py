import torch.optim as optim

class DQNConstants:
    EPISODES = 1
    BATCH_SIZE = 32
    TARGET_UPDATE = 500
    GAMMA = 0.99
    REPLAY_MEMORY_SIZE = 2700
    HIDDEN_LAYER_SIZE = 800
    LEARNING_RATE = 0.00025
    EPSILON_START = 1.0
    EPSILON_END = 0.1
    EPSILON_DECAY = 5000
    OPTIMIZER = optim.Adam
