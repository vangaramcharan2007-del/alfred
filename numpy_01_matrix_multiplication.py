import numpy as np

# 1. Create 3x5 array with sequential values from 1 to 15
a = np.arange(1, 16).reshape(3, 5)

# 2. Create an independent copy
b = a.copy()

# 3. Reshape the copy into a 5x3 matrix
b = b.reshape(5, 3)

print("First array (3x5):")
print(a)

print("\nReshaped copy (5x3):")
print(b)

# 4. Matrix multiplication (3x5) @ (5x3) -> (3x3)
result = np.dot(a, b)

print("\nMatrix multiplication result (3x3):")
print(result)
