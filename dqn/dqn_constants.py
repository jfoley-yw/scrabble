import torch.optim as optim

class DQNConstants:
    EPISODES = 50
    BATCH_SIZE = 32
    TARGET_UPDATE = 25
    GAMMA = 0.99
    REPLAY_MEMORY_SIZE = 90
    HIDDEN_LAYER_SIZE = 800
    LEARNING_RATE = 0.0001
    EPSILON_START = 1.0
    EPSILON_END = 0.1
    EPSILON_DECAY = 200
    OPTIMIZER = optim.RMSprop
