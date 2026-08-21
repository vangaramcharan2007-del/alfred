"""Day 1: Arrays & Hash Maps - Two Sum & Prefix Sum Pattern

Problem: Given an array of integers `nums` and an integer `target`,
return indices of the two numbers such that they add up to `target`.

Time Complexity:  O(N) - Single pass through the array.
Space Complexity: O(N) - Hash map storing visited elements.
"""

from typing import List, Tuple


def two_sum(nums: List[int], target: int) -> Tuple[int, int]:
    """Finds two indices whose values sum to target using a Hash Map."""
    seen = {}  # value -> index
    for index, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            return (seen[complement], index)
        seen[value] = index
    return (-1, -1)


def running_sum(nums: List[int]) -> List[int]:
    """Computes the prefix sum array in O(N) time and O(1) auxiliary space."""
    res = []
    current = 0
    for x in nums:
        current += x
        res.append(current)
    return res


if __name__ == "__main__":
    print("=" * 50)
    print("  JARVIS X DSA TUTOR - DAY 1: ARRAYS & HASH MAPS")
    print("=" * 50)

    test_nums = [2, 7, 11, 15]
    test_target = 9
    result = two_sum(test_nums, test_target)
    print(f"\nInput: nums = {test_nums}, target = {test_target}")
    print(f"Two Sum Indices: {result} -> Values: ({test_nums[result[0]]}, {test_nums[result[1]]})")
    assert result == (0, 1), "Two sum test failed!"

    prefix_res = running_sum([1, 2, 3, 4])
    print(f"Prefix Sum of [1, 2, 3, 4]: {prefix_res}")
    assert prefix_res == [1, 3, 6, 10], "Prefix sum test failed!"

    print("\n[SUCCESS]: All Day 1 DSA test cases passed flawlessly!")
