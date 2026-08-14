import numpy as np

# Prompt user for matrix dimension n
n = int(input("Enter n: "))

# Create n x n identity matrix
a = np.eye(n)

# Populate upper triangular elements
for i in range(n):
    a[i, i:] = np.arange(1, n - i + 1)

print("\nUpper triangular matrix:")
print(a.astype(int))
