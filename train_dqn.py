import torch
import matplotlib.pyplot as plt
from dqn.dqn_constants import DQNConstants
from dqn.dqn_player import DQNPlayer
from dqn.dqn_strategies import DQNTrainingStrategy
from dqn.dqn_helpers import DQNHelpers
from dqn.dqn_helpers import ReplayMemory
from dqn.dqn import DQN
from scrabbler.strategy import BaselineStrategy
from scrabbler.simulation import Simulation

# inspired by https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

# initialize global variables
num_episodes = DQNConstants.EPISODES
batch_size = DQNConstants.BATCH_SIZE
target_update = DQNConstants.TARGET_UPDATE
gamma = DQNConstants.GAMMA
# initialize action-replay memory
memory = ReplayMemory(DQNConstants.REPLAY_MEMORY_SIZE)
# initialize DQNs
policy_net = DQN(DQNHelpers.calculate_input_size(15), DQNConstants.HIDDEN_LAYER_SIZE)
target_net = DQN(DQNHelpers.calculate_input_size(15), DQNConstants.HIDDEN_LAYER_SIZE)
# initialize optimizer
optimizer = DQNConstants.OPTIMIZER(policy_net.parameters(), lr = DQNConstants.LEARNING_RATE)
# keep track of results
results = []
# keep track of losses
losses = []
# keep track of total steps taken
total_steps = 0

for i_episode in range(num_episodes):
    # initialize dqn strategy
    dqn_strategy = DQNTrainingStrategy(policy_net, DQNConstants.EPSILON_START, DQNConstants.EPSILON_END, DQNConstants.EPSILON_DECAY)
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
        if cont:
            action_taken = simulation.most_recent_move.word
            action = DQNHelpers.get_action_vector(action_taken)
            # simulate Baseline agent's action (this is part of the MDP environment)
            cont = simulation.simulate_step()
        else:
            action = DQNHelpers.get_empty_action_vector()

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

        loss = DQNHelpers.optimize_model(policy_net, target_net, memory, gamma, batch_size, optimizer)
        losses.append(loss)
        step += 1
        total_steps += 1

        # update target network when necessary
        if total_steps % target_update == 0:
            target_net.load_state_dict(policy_net.state_dict())

    results.append((dqn_player.get_score(), baseline_player.get_score()))

    print("EPISODE %d COMPLETED!" % (i_episode))

# construct iterations vs. scores plot and iterations vs. losses plot
dqn_scores = [result[0] for result in results]
baseline_scores = [result[1] for result in results]
episodes = [i for i in range(num_episodes)]
steps = [i for i in range(0, total_steps, 10)]
losses = [losses[i] for i in range(0, total_steps, 10)]

plt.figure()

plt.subplot(211)
plt.plot(episodes, dqn_scores, episodes, baseline_scores)

plt.subplot(212)
plt.plot(steps, losses)
plt.savefig('dqn_plots.png')
