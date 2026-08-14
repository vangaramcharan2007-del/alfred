import numpy as np

# Prompt user for matrix size
n = int(input("Enter size of matrix: "))

# Generate random n x n matrix with integers between 1 and 9
A = np.random.randint(1, 10, (n, n))

print("\nMatrix A:")
print(A)

# Compute Rank, Determinant, and Trace
rank = np.linalg.matrix_rank(A)
det = np.linalg.det(A)
trace_A = np.trace(A)

# Compute Inverse and Trace of Inverse if non-singular
if det != 0:
    A_inv = np.linalg.inv(A)
    trace_inv = np.trace(A_inv)
else:
    A_inv = None
    trace_inv = 0

# Apply specified formula: result = rank(A) + det(A) + trace(A) * trace(A^-1)
result = rank + det + (trace_A * trace_inv)

print(f"\nRank = {rank}")
print(f"Determinant = {det:.4f}")
print(f"Trace of A = {trace_A}")

if A_inv is not None:
    print("\nInverse of A:")
    print(A_inv)
else:
    print("\nInverse does not exist (singular matrix)")

print(f"\nResult = {result:.4f}")
