import torch.optim as optim

class DQNConstants:
    EPISODES = 100
    BATCH_SIZE = 10
    TARGET_UPDATE = 10
    GAMMA = 0.99
    REPLAY_MEMORY_SIZE = 50
    HIDDEN_LAYER_SIZE = 100
    LEARNING_RATE = 0.00025
    EPSILON_START = 1.0
    EPSILON_END = 0.1
    EPSILON_DECAY = 50
    OPTIMIZER = optim.Adam
