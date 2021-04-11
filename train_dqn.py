import torch
import torch.optim as optim
from dqn.dqn_player import DQNPlayer
from dqn.dqn_strategies import DQNTrainingStrategy
from dqn.dqn_helpers import DQNHelpers
from dqn.dqn_helpers import ReplayMemory
from dqn.dqn import DQN
from scrabbler.strategy import BaselineStrategy
from scrabbler.simulation import Simulation

# inspired by https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

# initialize global variables
num_episodes = 2
batch_size = 5
target_update = 1
gamma = 0.999
# initialize action-replay memory
memory = ReplayMemory(100)
# initialize DQNs
policy_net = DQN(DQNHelpers.calculate_input_size(15), 100)
target_net = DQN(DQNHelpers.calculate_input_size(15), 100)
# initialize optimizer
optimizer = optim.RMSprop(policy_net.parameters())

for i_episode in range(num_episodes):
    # initialize dqn strategy where eps_start = 0.9, eps_end = 0.05, and eps_decay = 200
    dqn_strategy = DQNTrainingStrategy(policy_net, 0.9, 0.05, 200)
    dqn_player = DQNPlayer(dqn_strategy)
    baseline_strategy = BaselineStrategy()
    baseline_player = DQNPlayer(baseline_strategy)
    simulation = Simulation(dqn_player, baseline_player, 0)
    step = 0
    cont = True

    # start the episode
    while cont:
        # calculate MDP state
        state = DQNHelpers.get_state_vector(simulation.game)

        # perform and record DQN agent's action
        cont = simulation.simulate_step()
        action_taken = simulation.most_recent_move.word
        action = DQNHelpers.get_action_vector(action_taken)
        if cont:
            # simulate Baseline agent's action (this is part of the MDP environment)
            cont = simulation.simulate_step()

        # calculate MDP reward
        new_score_diff = dqn_player.get_score() - baseline_player.get_score()
        if step >= 2:
            old_score_diff = dqn_player.get_old_score() - baseline_player.get_old_score()
        else:
            old_score_diff = 0
        reward = torch.tensor([[new_score_diff - old_score_diff]], dtype = torch.float)

        # calculate MDP next state and next actions
        next_actions = []
        if cont:
            next_state = DQNHelpers.get_state_vector(simulation.game)
            for move in simulation.game.find_valid_moves(dqn_player.get_rack()):
                next_actions.append(DQNHelpers.get_action_vector(move.word))
        else:
            next_state = None

       # save MDP transition in action-replay memory
        memory.push(state, action, next_state, reward, next_actions)

        DQNHelpers.optimize_model(policy_net, target_net, memory, gamma, batch_size, optimizer)
        step += 1

    # update target network when necessary
    if i_episode % target_update == 0:
        target_net.load_state_dict(policy_net.state_dict())
