import matplotlib.pyplot as plt
import math

# this is a helper script to properly choose the epsilon rate of decay during DQN training

start = 1.0
end = 0.1
decay = 14000
steps = 80000

thresholds = []

for i in range(steps):
    threshold = end + (start - end) * \
        math.exp(-1 * i / decay)
    thresholds.append(threshold)

iters = [i for i in range(steps)]

plt.plot(iters, thresholds)
plt.show()
