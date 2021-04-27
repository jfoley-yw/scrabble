import torch.optim as optim

class DQNConstants:
    EPISODES = 1000
    BATCH_SIZE = 64
    TARGET_UPDATE = 100
    GAMMA = 0.99
    REPLAY_MEMORY_SIZE = 100
    HIDDEN_LAYER_SIZE = 20
    LEARNING_RATE = 0.00001
    EPSILON_START = 1.0
    EPSILON_END = 0.1
    EPSILON_DECAY = 500
    OPTIMIZER = optim.Adam
