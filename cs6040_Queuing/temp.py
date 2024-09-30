import numpy as np

np.random.seed(0)

count = 0
for _ in range(1, 101):
    if np.random.binomial(n=1, p=0.1):
        count+=1

print(count)