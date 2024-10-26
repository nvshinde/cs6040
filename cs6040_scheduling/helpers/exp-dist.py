# import numpy as np
# import seaborn as sns
# import pandas as pd
# import matplotlib.pyplot as plt

# np.random.seed(0)

# N = 1000
# mean = 10

# samples = np.random.exponential(scale=1/mean, size=N)
# df = pd.DataFrame(samples, columns=['Sample'])

# sns.set_theme()
# sns.relplot(data=samples)
# plt.show()

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

np.random.seed(0)

N = 1000
mean = 10

# Generate samples
samples = []
for i in range(N):
    sample = np.random.exponential(scale=1/mean)
    samples.append(sample)

print(samples)
# Convert to a DataFrame for Seaborn
df = pd.DataFrame(samples, columns=['Sample'])

# Set the theme for the plot
sns.set_theme()

# Create a histogram to visualize the distribution
plt.figure(figsize=(8, 5))
sns.histplot(df['Sample'], bins=20, kde=True)
plt.title('Histogram of Exponential Samples')
plt.xlabel('Sample Value')
plt.ylabel('Frequency')
plt.show()
