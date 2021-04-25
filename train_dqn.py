import torch
import collections
import matplotlib.pyplot as plt
from dqn.dqn_constants_4_x_4 import DQNConstants
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
policy_net = DQN(DQNScrabbleHelpers.calculate_input_size(4), DQNConstants.HIDDEN_LAYER_SIZE, 20)
target_net = DQN(DQNScrabbleHelpers.calculate_input_size(4), DQNConstants.HIDDEN_LAYER_SIZE, 20)
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
    state = DQNScrabbleHelpers.get_state_vector(observation.state)
    score = 0

    # start the episode
    while not done:
        action = DQNScrabbleHelpers.select_training_action(observation, epsilon_start, epsilon_end, epsilon_decay, total_steps, policy_net)

        observation, reward, done, score = env.step(action)
        rewards.append(reward)

        action = torch.tensor([[action]], dtype = torch.int64) # need int64 for indexing in torch.gater(dim, index)
        reward = torch.tensor([[reward]], dtype = torch.float)

        if done:
            next_state = None
        else:
            next_state = DQNScrabbleHelpers.get_state_vector(observation.state)
        
        action_mask = torch.tensor([observation.action_mask], dtype = torch.float)

        # save MDP transition in action-replay memory
        memory.push(state, action, next_state, reward, action_mask)

        loss = DQNScrabbleHelpers.optimize_model(policy_net, target_net, memory, gamma, batch_size, optimizer)
        losses.append(loss)

        state = next_state
        total_steps += 1

        # update target network when necessary
        if total_steps % target_update == 0:
            target_net.load_state_dict(policy_net.state_dict())

    results.append(score)

    print("EPISODE %d COMPLETED!" % (i_episode))

# save policy net parameters to a file
torch.save(policy_net.state_dict(), './dqn/models/policy_net_final.pt')

# reward_dict = collections.defaultdict(int)
# for i in range(len(rewards)):
#     reward_dict[rewards[i]] += 1

# scores_dict = collections.defaultdict(int)
# for i in range(len(results)):
#     scores_dict[results[i]] += 1

print(total_steps)
print(total_steps / num_episodes)

# aggregate data for plotting
episodes = [i for i in range(0, num_episodes, 10)]
results = [results[i] for i in range(0, num_episodes, 10)]
loss_steps = [i for i in range(0, total_steps, 10)]
losses = [losses[i] for i in range(0, total_steps, 10)]
reward_steps = [i for i in range(0, total_steps, 10)]
rewards = [rewards[i] for i in range(0, total_steps, 10)]

# construct episodes vs. scores plot, iterations vs. losses plot, iterations vs. rewards plot
_, axis = plt.subplots(2, 2)
# axis[0, 0].bar(list(scores_dict.keys()), list(scores_dict.values()))
axis[0, 0].plot(episodes, results)
axis[0, 1].plot(loss_steps, losses)
axis[1, 0].plot(reward_steps, rewards)
# axis[1,0].bar(list(reward_dict.keys()), list(reward_dict.values()))
plt.savefig('./dqn/plots/dqn_plots.png')
