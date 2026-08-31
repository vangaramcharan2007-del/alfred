"""
==============================================================================
   ALFRED OS — DSA PRACTICE MODULE 1: ARRAYS & TWO POINTERS
   Interactive Practice Suite — Alfred is actively watching this file.
   Save (Ctrl+S) anytime to automatically run tests and receive spoken audio hints!
==============================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from typing import List


# ----------------------------------------------------------------------------
# CHALLENGE 1: Two Sum (LeetCode #1 - Easy)
# ----------------------------------------------------------------------------
# Given an array of integers nums and an integer target, return indices of the
# two numbers such that they add up to target.
# You may assume that each input would have exactly one solution.
# Target Time Complexity: O(n) | Target Space Complexity: O(n)
# ----------------------------------------------------------------------------
def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Find two numbers in nums that add up to target and return their indices.
    
    HINT from Alfred: Use a hash map (dictionary) to store seen values and their indices!
    """
    # Write your solution here:
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []


# ----------------------------------------------------------------------------
# CHALLENGE 2: Container With Most Water (LeetCode #11 - Medium)
# ----------------------------------------------------------------------------
# You are given an integer array height of length n. There are n vertical lines.
# Find two lines that together with the x-axis form a container that holds the most water.
# Target Time Complexity: O(n) | Target Space Complexity: O(1)
# ----------------------------------------------------------------------------
def max_area(height: List[int]) -> int:
    """
    Calculate maximum water container area.
    
    HINT from Alfred: Start with two pointers at the ends (left=0, right=len-1)
    and move the pointer pointing to the shorter line inward!
    """
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        width = right - left
        h = min(height[left], height[right])
        max_water = max(max_water, width * h)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_water


# ----------------------------------------------------------------------------
# CHALLENGE 3: Valid Palindrome (LeetCode #125 - Easy)
# ----------------------------------------------------------------------------
# Given a string s, return true if it is a palindrome, considering only
# alphanumeric characters and ignoring cases.
# Target Time Complexity: O(n) | Target Space Complexity: O(1)
# ----------------------------------------------------------------------------
def is_palindrome(s: str) -> bool:
    """
    Return True if alphanumeric characters form a palindrome.
    """
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True


# ----------------------------------------------------------------------------
# TEST HARNESS — Alfred executes these tests automatically on save
# ----------------------------------------------------------------------------
def run_all_tests():
    print("\n--- Running Module 1 Tests ---")
    
    # Test 1
    assert two_sum([2, 7, 11, 15], 9) == [0, 1], "Test 1 failed: [2, 7, 11, 15], target=9"
    assert two_sum([3, 2, 4], 6) == [1, 2], "Test 2 failed: [3, 2, 4], target=6"
    assert two_sum([3, 3], 6) == [0, 1], "Test 3 failed: [3, 3], target=6"
    print("[OK] Challenge 1 (Two Sum): PASSED")

    # Test 2
    assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49, "Test 1 failed: max_area standard"
    assert max_area([1, 1]) == 1, "Test 2 failed: max_area minimal"
    print("[OK] Challenge 2 (Container With Most Water): PASSED")

    # Test 3
    assert is_palindrome("A man, a plan, a canal: Panama") is True, "Test 1 failed: palindrome true"
    assert is_palindrome("race a car") is False, "Test 2 failed: palindrome false"
    assert is_palindrome(" ") is True, "Test 3 failed: empty/space palindrome"
    print("[OK] Challenge 3 (Valid Palindrome): PASSED")

    print("\n[SUCCESS] ALL MODULE 1 CHALLENGES PASSED PERFECTLY!\n")


if __name__ == "__main__":
    run_all_tests()
