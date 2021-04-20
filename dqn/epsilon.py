import matplotlib.pyplot as plt
import math

start = 1.0
end = 0.1
decay = 40000
steps = 200000

thresholds = []

for i in range(steps):
    threshold = end + (start - end) * \
        math.exp(-1 * i / decay)
    thresholds.append(threshold)

iters = [i for i in range(steps)]

plt.plot(iters, thresholds)
plt.show()
