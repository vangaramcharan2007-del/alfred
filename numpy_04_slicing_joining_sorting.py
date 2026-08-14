import numpy as np

# 1. Prompt user for array size and element inputs
n = int(input("Enter size: "))
a = np.array(list(map(int, input("Enter elements (space-separated): ").split())))

# 2. Construct second array b containing sequential integers from 1 to n
b = np.arange(1, n + 1)

# 3. Partition array a and array b into halves and parity components
half = n // 2

first_half = a[:half]
odd_numbers = b[b % 2 != 0]
part1 = np.concatenate((first_half, odd_numbers))

second_half = a[half:]
even_numbers = b[b % 2 == 0]
part2 = np.concatenate((second_half, even_numbers))

# 4. Join and sort the composite array
result = np.concatenate((part1, part2))
result = np.sort(result)

print("\nFirst array (a):", a)
print("Second array (b):", b)
print("Part 1 (first half + odd):", part1)
print("Part 2 (second half + even):", part2)
print("Final sorted array:", result)
