import torch
import matplotlib.pyplot as plt
from dqn.dqn_constants import DQNConstants
from dqn.dqn_scrabble_helpers import DQNScrabbleHelpers
from dqn.dqn_scrabble_helpers import ReplayMemory
from dqn.dqn import DQN
from dqn.dqn_scrabble_environment import DQNScrabbleEnvironment

# inspired by https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

# initialize global variables
num_episodes = DQNConstants.EPISODES
batch_size = DQNConstants.BATCH_SIZE
target_update = DQNConstants.TARGET_UPDATE
gamma = DQNConstants.GAMMA
epsilon_start = DQNConstants.EPSILON_START
epsilon_end = DQNConstants.EPSILON_END
epsilon_decay = DQNConstants.EPSILON_DECAY
# initialize action-replay memory
memory = ReplayMemory(DQNConstants.REPLAY_MEMORY_SIZE)
# initialize DQNs
policy_net = DQN(DQNHelpers.calculate_input_size(5), DQNConstants.HIDDEN_LAYER_SIZE)
target_net = DQN(DQNHelpers.calculate_input_size(5), DQNConstants.HIDDEN_LAYER_SIZE)
# initialize optimizer
optimizer = DQNConstants.OPTIMIZER(policy_net.parameters(), lr = DQNConstants.LEARNING_RATE)
# keep track of results
results = []
# keep track of losses
losses = []
# keep track of rewards
rewards = []
# keep track of total steps taken
total_steps = 0
# initialize environment
env = DQNScrabbleEnvironment()

for i_episode in range(num_episodes):
    observation, done = env.reset()

    # start the episode
    while not done:
        state = observation.state
        action = DQNScrabbleHelpers.select_training_action(observation, epsilon_start, epsilon_end, epsilon_decay, total_steps, policy_net)

        observation, reward, done, _ = env.step(action)
        rewards.append(torch.tensor([[reward]], dtype = torch.float))

        if done:
            next_state = None
            action_mask = None
        else:
            next_state = DQNScrabbleHelpers.get_state_vector(observation.state)
            action_mask = torch.tensor([observation.action_mask], dype = torch.float)

        # save MDP transition in action-replay memory
        memory.push(state, action, next_state, reward, action_mask)

        loss = DQNHelpers.optimize_model(policy_net, target_net, memory, gamma, batch_size, optimizer)
        losses.append(loss)

        total_steps += 1

        # update target network when necessary
        if total_steps % target_update == 0:
            target_net.load_state_dict(policy_net.state_dict())

    results.append(env.get_final_score())

    print("EPISODE %d COMPLETED!" % (i_episode))

# save policy net parameters to a file
torch.save(policy_net.state_dict(), './dqn/models/policy_net_final.pt')

# aggregate data for plotting
episodes = [i for i in range(num_episodes)]
steps = [i for i in range(0, total_steps, 10)]
losses = [losses[i] for i in range(0, total_steps, 10)]
rewards = [rewards[i] for i in range(0, total_steps, 10)]

# construct episodes vs. scores plot, iterations vs. losses plot, iterations vs. rewards plot
_, axis = plt.subplots(2, 2)
axis[0, 0].plot(episodes, results)
axis[0, 1].plot(steps, losses)
axis[1,0].plot(steps, rewards)
plt.savefig('./dqn/plots/dqn_plots.png')
