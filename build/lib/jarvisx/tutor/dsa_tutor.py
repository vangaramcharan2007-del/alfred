"""Daily Interactive DSA Tutor Engine for Jarvis X.

Coordinates multi-modal learning:
1. Spoken voice lessons & conceptual briefings via Alfred TTS.
2. Live VS Code file generation and editor focus.
3. Relevant curated video tutorials launched in browser.
4. Persistent streak and curriculum progress tracking in SQLite/JSON memory.
"""

from __future__ import annotations
import os
import json
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvisx.automation.vscode_controller import VSCodeController


CURRICULUM_ROADMAP: List[Dict[str, Any]] = [
    {
        "day": 1,
        "topic": "Arrays & Hash Maps (Two Sum, Prefix Sums)",
        "slug": "arrays_and_hashmaps",
        "description": "Day 1 covers the foundation of all DSA: contiguous array traversal, O(1) hash map lookups, and the classic Two Sum pattern using complement lookups.",
        "video_query": "neetcode arrays and hashing two sum",
        "video_url": "https://www.youtube.com/results?search_query=neetcode+arrays+and+hashing+two+sum",
        "code": '''"""Day 1: Arrays & Hash Maps - Two Sum & Prefix Sum Pattern

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
    print(f"\\nInput: nums = {test_nums}, target = {test_target}")
    print(f"Two Sum Indices: {result} -> Values: ({test_nums[result[0]]}, {test_nums[result[1]]})")
    assert result == (0, 1), "Two sum test failed!"

    prefix_res = running_sum([1, 2, 3, 4])
    print(f"Prefix Sum of [1, 2, 3, 4]: {prefix_res}")
    assert prefix_res == [1, 3, 6, 10], "Prefix sum test failed!"

    print("\\n[SUCCESS]: All Day 1 DSA test cases passed flawlessly!")
'''
    },
    {
        "day": 2,
        "topic": "Two Pointers & Sliding Window",
        "slug": "two_pointers_sliding_window",
        "description": "Day 2 explores Two Pointers and Sliding Window techniques to solve subarray and palindrome problems in O(N) time without quadratic nested loops.",
        "video_query": "neetcode sliding window longest substring",
        "video_url": "https://www.youtube.com/results?search_query=neetcode+sliding+window+longest+substring",
        "code": '''"""Day 2: Two Pointers & Sliding Window

Problems:
1. Valid Palindrome with Two Pointers.
2. Longest Substring Without Repeating Characters (Sliding Window).

Time Complexity:  O(N)
Space Complexity: O(min(N, M)) where M is character set size.
"""


def is_palindrome(s: str) -> bool:
    """Check if string is palindrome ignoring non-alphanumeric chars."""
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


def length_of_longest_substring(s: str) -> int:
    """Finds length of longest non-repeating substring via Sliding Window."""
    char_index = {}
    left = 0
    max_len = 0

    for right, char in enumerate(s):
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1
        char_index[char] = right
        max_len = max(max_len, right - left + 1)

    return max_len


if __name__ == "__main__":
    print("=" * 50)
    print("  JARVIS X DSA TUTOR - DAY 2: TWO POINTERS & SLIDING WINDOW")
    print("=" * 50)

    s1 = "A man, a plan, a canal: Panama"
    print(f"Palindrome '{s1}': {is_palindrome(s1)}")
    assert is_palindrome(s1) is True

    s2 = "abcabcbb"
    longest = length_of_longest_substring(s2)
    print(f"Longest non-repeating in '{s2}': {longest}")
    assert longest == 3

    print("\\n[SUCCESS]: All Day 2 DSA test cases passed flawlessly!")
'''
    },
    {
        "day": 3,
        "topic": "Singly & Doubly Linked Lists",
        "slug": "linked_lists",
        "description": "Day 3 focuses on Linked Lists: pointer manipulations, fast and slow runner pointers for cycle detection, and list reversal in O(N) time and O(1) space.",
        "video_query": "neetcode reverse linked list fast and slow pointers",
        "video_url": "https://www.youtube.com/results?search_query=neetcode+reverse+linked+list",
        "code": '''"""Day 3: Linked Lists - Reversal & Fast/Slow Cycle Detection

Problem:
1. Reverse a singly linked list in-place.
2. Detect cycle in a linked list using Floyd's Tortoise and Hare algorithm.
"""

from typing import Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next


def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """Reverses a singly linked list in O(N) time and O(1) space."""
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev


def has_cycle(head: Optional[ListNode]) -> bool:
    """Floyd's cycle detection algorithm with slow and fast pointers."""
    slow, fast = head, head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False


if __name__ == "__main__":
    print("=" * 50)
    print("  JARVIS X DSA TUTOR - DAY 3: LINKED LISTS")
    print("=" * 50)

    # Construct 1 -> 2 -> 3 -> 4 -> 5
    head = ListNode(1, ListNode(2, ListNode(3, ListNode(4, ListNode(5)))))
    rev = reverse_list(head)
    
    vals = []
    curr = rev
    while curr:
        vals.append(curr.val)
        curr = curr.next
    print(f"Reversed list values: {vals}")
    assert vals == [5, 4, 3, 2, 1]

    print("\\n[SUCCESS]: Day 3 Linked List reversal passed!")
'''
    },
    {
        "day": 4,
        "topic": "Stacks, Queues & Monotonic Stack",
        "slug": "stacks_and_queues",
        "description": "Day 4 covers LIFO Stack and FIFO Queue architectures, Valid Parentheses matching, and Next Greater Element using Monotonic Stacks.",
        "video_query": "neetcode valid parentheses monotonic stack",
        "video_url": "https://www.youtube.com/results?search_query=neetcode+valid+parentheses+stack",
        "code": '''"""Day 4: Stacks & Queues - Valid Parentheses & Monotonic Stack."""

from typing import List


def is_valid_parentheses(s: str) -> bool:
    """Validates matched brackets using a LIFO Stack."""
    stack = []
    mapping = {")": "(", "}": "{", "]": "["}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    return not stack


def next_greater_element(nums: List[int]) -> List[int]:
    """Finds next greater element for each number using Monotonic Stack in O(N)."""
    n = len(nums)
    res = [-1] * n
    stack = []  # store indices of monotonic decreasing elements

    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            res[idx] = nums[i]
        stack.append(i)
    return res


if __name__ == "__main__":
    print("=" * 50)
    print("  JARVIS X DSA TUTOR - DAY 4: STACKS & QUEUES")
    print("=" * 50)

    assert is_valid_parentheses("({[]})") is True
    assert is_valid_parentheses("([)]") is False
    print("Valid Parentheses tests passed!")

    nge = next_greater_element([2, 1, 2, 4, 3])
    print(f"Next Greater Elements for [2, 1, 2, 4, 3]: {nge}")
    assert nge == [4, 2, 4, -1, -1]

    print("\\n[SUCCESS]: Day 4 Stack test cases passed!")
'''
    },
    {
        "day": 5,
        "topic": "Binary Search & Search Space Reduction",
        "slug": "binary_search",
        "description": "Day 5 masters Binary Search: exact lookups, finding first/last occurrences, and applying binary search on monotonic answer spaces in O(log N) time.",
        "video_query": "neetcode binary search search a 2d matrix",
        "video_url": "https://www.youtube.com/results?search_query=neetcode+binary+search",
        "code": '''"""Day 5: Binary Search & Search Space Reduction."""

from typing import List


def binary_search(nums: List[int], target: int) -> int:
    """Standard binary search returning index of target or -1."""
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


if __name__ == "__main__":
    print("=" * 50)
    print("  JARVIS X DSA TUTOR - DAY 5: BINARY SEARCH")
    print("=" * 50)

    arr = [-1, 0, 3, 5, 9, 12]
    idx = binary_search(arr, 9)
    print(f"Index of 9 in {arr}: {idx}")
    assert idx == 4

    print("\\n[SUCCESS]: Day 5 Binary Search passed!")
'''
    }
]


class DSATutorEngine:
    """Manages daily curriculum, workspace generation, VS Code launching, and video delivery."""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()
        self.dsa_dir = self.workspace_root / "dsa"
        self.dsa_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.workspace_root / "var" / "dsa_progress.json"
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.vscode = VSCodeController(workspace_dir=str(self.workspace_root))

    def get_progress(self) -> Dict[str, Any]:
        """Load current DSA curriculum progress from disk."""
        if self.progress_file.exists():
            try:
                return json.loads(self.progress_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "current_day": 1,
            "completed_days": [],
            "streak_count": 1,
            "last_active_date": ""
        }

    def save_progress(self, progress: Dict[str, Any]) -> None:
        """Save progress to disk and record into memory."""
        try:
            self.progress_file.write_text(json.dumps(progress, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_lesson(self, day: int) -> Dict[str, Any]:
        """Fetch lesson definition for a given day."""
        for item in CURRICULUM_ROADMAP:
            if item["day"] == day:
                return item
        # Fallback to day 1 if out of range
        return CURRICULUM_ROADMAP[0]

    def launch_daily_lesson(self, day: Optional[int] = None, open_video: bool = True, open_vscode: bool = True) -> Dict[str, Any]:
        """Execute full multi-modal lesson sequence: Code File + VS Code + Video + Voice Briefing."""
        progress = self.get_progress()
        target_day = day if day is not None else progress.get("current_day", 1)
        lesson = self.get_lesson(target_day)

        # 1. Create lesson code file in workspace/dsa/
        filename = f"day_{lesson['day']}_{lesson['slug']}.py"
        file_path = self.dsa_dir / filename
        file_path.write_text(lesson["code"], encoding="utf-8")

        # 2. Launch VS Code and bring to foreground
        vscode_status = "SKIPPED"
        if open_vscode:
            try:
                self.vscode.focus_or_launch(str(file_path))
                vscode_status = "LAUNCHED"
            except Exception as e:
                vscode_status = f"ERROR: {e}"

        # 3. Launch YouTube Video Tutorial in browser
        video_status = "SKIPPED"
        if open_video:
            try:
                webbrowser.open(lesson["video_url"])
                video_status = "OPENED"
            except Exception as e:
                video_status = f"ERROR: {e}"

        # 4. Update progress
        progress["current_day"] = target_day
        if target_day not in progress.get("completed_days", []):
            progress["completed_days"].append(target_day)
        self.save_progress(progress)

        spoken_script = (
            f"Welcome to Day {lesson['day']} of your Data Structures and Algorithms Master Course, Sir! "
            f"Today's topic is {lesson['topic']}. {lesson['description']} "
            f"I have created the lesson file {filename} in your VS Code editor and opened the curated video lecture on your screen. "
            f"Let's write and run the code together!"
        )

        return {
            "status": "SUCCESS",
            "day": target_day,
            "topic": lesson["topic"],
            "filename": str(file_path.relative_to(self.workspace_root)),
            "video_url": lesson["video_url"],
            "spoken_script": spoken_script,
            "vscode_status": vscode_status,
            "video_status": video_status,
        }
