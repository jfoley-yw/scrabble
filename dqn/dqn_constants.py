import torch.optim as optim

class DQNConstants:
    EPISODES = 500
    BATCH_SIZE = 32
    TARGET_UPDATE = 100
    GAMMA = 0.99
    REPLAY_MEMORY_SIZE = 900
    HIDDEN_LAYER_SIZE = 800
    LEARNING_RATE = 0.001
    EPSILON_START = 1.0
    EPSILON_END = 0.1
    EPSILON_DECAY = 1900
    OPTIMIZER = optim.RMSprop
