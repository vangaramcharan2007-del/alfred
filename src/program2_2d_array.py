import numpy as np

C = np.array([[1, 6, 3],
              [8, 9, 5],
              [7, 2, 4]])

print("Array C:")
print(C)

print("C[0,0] =", C[0,0])
print("C[2,0] =", C[2,0])
print("C[1,1:] =", C[1,1:])
print("C[1:,1:] =")
print(C[1:,1:])
print("C[:-1,:-1] =")
print(C[:-1,:-1])
