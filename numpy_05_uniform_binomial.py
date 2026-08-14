import numpy as np

# 1. Prompt user for size
n = int(input("Enter size: "))

# 2. Generate uniform random continuous values in the range [1, 10)
a = np.random.uniform(1, 10, n)
print("\nUniform random array (a):")
print(a)

# 3. Calculate empirical probability of event (value > 7)
p = float(np.mean(a > 7))
print(f"\nProbability of success (p = P(X > 7)): {p:.4f}")

# 4. Generate Binomial Distribution sample (n_trials=1, prob=p, size=1000)
binomial = np.random.binomial(1, p, 1000)
print("\nBinomial distribution sample (first 30 values):")
print(binomial[:30])

# 5. Compute overall empirical probability of success
overall_probability = float(np.mean(binomial))
print(f"\nOverall sample probability of success: {overall_probability:.4f}")
