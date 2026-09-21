# 🏆 Top 22 LeetCode Medium/Hard Data Structures Solutions in C
> **Target:** SRM LLJ1 Coursework (>20 Medium/Hard Data Structures problems in C for full 5/5 marks).

---

## 📌 TABLE OF CONTENTS
1. [LC 75 - Sort Colors (Medium)](#1-lc-75---sort-colors-medium)
2. [LC 33 - Search in Rotated Sorted Array (Medium)](#2-lc-33---search-in-rotated-sorted-array-medium)
3. [LC 34 - Find First and Last Position of Element in Sorted Array (Medium)](#3-lc-34---find-first-and-last-position-in-sorted-array-medium)
4. [LC 53 - Maximum Subarray (Medium)](#4-lc-53---maximum-subarray-medium)
5. [LC 189 - Rotate Array (Medium)](#5-lc-189---rotate-array-medium)
6. [LC 287 - Find the Duplicate Number (Medium)](#6-lc-287---find-the-duplicate-number-medium)
7. [LC 153 - Find Minimum in Rotated Sorted Array (Medium)](#7-lc-153---find-minimum-in-rotated-sorted-array-medium)
8. [LC 215 - Kth Largest Element in an Array (Medium)](#8-lc-215---kth-largest-element-in-an-array-medium)
9. [LC 11 - Container With Most Water (Medium)](#9-lc-11---container-with-most-water-medium)
10. [LC 15 - 3Sum (Medium)](#10-lc-15---3sum-medium)
11. [LC 56 - Merge Intervals (Medium)](#11-lc-56---merge-intervals-medium)
12. [LC 2 - Add Two Numbers (Medium)](#12-lc-2---add-two-numbers-medium)
13. [LC 19 - Remove Nth Node From End of List (Medium)](#13-lc-19---remove-nth-node-from-end-of-list-medium)
14. [LC 24 - Swap Nodes in Pairs (Medium)](#14-lc-24---swap-nodes-in-pairs-medium)
15. [LC 61 - Rotate List (Medium)](#15-lc-61---rotate-list-medium)
16. [LC 82 - Remove Duplicates from Sorted List II (Medium)](#16-lc-82---remove-duplicates-from-sorted-list-ii-medium)
17. [LC 86 - Partition List (Medium)](#17-lc-86---partition-list-medium)
18. [LC 92 - Reverse Linked List II (Medium)](#18-lc-92---reverse-linked-list-ii-medium)
19. [LC 142 - Linked List Cycle II (Medium)](#19-lc-142---linked-list-cycle-ii-medium)
20. [LC 148 - Sort List (Medium)](#20-lc-148---sort-list-medium)
21. [LC 143 - Reorder List (Medium)](#21-lc-143---reorder-list-medium)
22. [LC 23 - Merge k Sorted Lists (Hard)](#22-lc-23---merge-k-sorted-lists-hard)

---

### 1. LC 75 - Sort Colors (Medium)
**Link:** https://leetcode.com/problems/sort-colors/  
```c
void sortColors(int* nums, int numsSize) {
    int low = 0, mid = 0, high = numsSize - 1;
    while (mid <= high) {
        if (nums[mid] == 0) {
            int temp = nums[low];
            nums[low++] = nums[mid];
            nums[mid++] = temp;
        } else if (nums[mid] == 1) {
            mid++;
        } else {
            int temp = nums[mid];
            nums[mid] = nums[high];
            nums[high--] = temp;
        }
    }
}
```

---

### 2. LC 33 - Search in Rotated Sorted Array (Medium)
**Link:** https://leetcode.com/problems/search-in-rotated-sorted-array/  
```c
int search(int* nums, int numsSize, int target) {
    int left = 0, right = numsSize - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) return mid;
        
        if (nums[left] <= nums[mid]) {
            if (nums[left] <= target && target < nums[mid])
                right = mid - 1;
            else
                left = mid + 1;
        } else {
            if (nums[mid] < target && target <= nums[right])
                left = mid + 1;
            else
                right = mid - 1;
        }
    }
    return -1;
}
```

---

### 3. LC 34 - Find First and Last Position in Sorted Array (Medium)
**Link:** https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/  
```c
int* searchRange(int* nums, int numsSize, int target, int* returnSize) {
    *returnSize = 2;
    int* res = (int*)malloc(sizeof(int) * 2);
    res[0] = -1;
    res[1] = -1;
    if (numsSize == 0) return res;

    // Find first
    int left = 0, right = numsSize - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] >= target) right = mid - 1;
        else left = mid + 1;
    }
    if (left < numsSize && nums[left] == target) res[0] = left;
    else return res;

    // Find last
    right = numsSize - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] <= target) left = mid + 1;
        else right = mid - 1;
    }
    res[1] = right;
    return res;
}
```

---

### 4. LC 53 - Maximum Subarray (Medium)
**Link:** https://leetcode.com/problems/maximum-subarray/  
```c
int maxSubArray(int* nums, int numsSize) {
    int max_sum = nums[0];
    int curr = nums[0];
    for (int i = 1; i < numsSize; i++) {
        curr = (nums[i] > curr + nums[i]) ? nums[i] : curr + nums[i];
        if (curr > max_sum) max_sum = curr;
    }
    return max_sum;
}
```

---

### 5. LC 189 - Rotate Array (Medium)
**Link:** https://leetcode.com/problems/rotate-array/  
```c
void reverse(int* nums, int start, int end) {
    while (start < end) {
        int temp = nums[start];
        nums[start++] = nums[end];
        nums[end--] = temp;
    }
}

void rotate(int* nums, int numsSize, int k) {
    k %= numsSize;
    reverse(nums, 0, numsSize - 1);
    reverse(nums, 0, k - 1);
    reverse(nums, k, numsSize - 1);
}
```

---

### 6. LC 287 - Find the Duplicate Number (Medium)
**Link:** https://leetcode.com/problems/find-the-duplicate-number/  
```c
int findDuplicate(int* nums, int numsSize) {
    int slow = nums[0];
    int fast = nums[0];
    do {
        slow = nums[slow];
        fast = nums[nums[fast]];
    } while (slow != fast);
    
    fast = nums[0];
    while (slow != fast) {
        slow = nums[slow];
        fast = nums[fast];
    }
    return slow;
}
```

---

### 7. LC 153 - Find Minimum in Rotated Sorted Array (Medium)
**Link:** https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/  
```c
int findMin(int* nums, int numsSize) {
    int left = 0, right = numsSize - 1;
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] > nums[right]) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    return nums[left];
}
```

---

### 8. LC 215 - Kth Largest Element in an Array (Medium)
**Link:** https://leetcode.com/problems/kth-largest-element-in-an-array/  
```c
int cmp(const void* a, const void* b) {
    return (*(int*)b - *(int*)a);
}

int findKthLargest(int* nums, int numsSize, int k) {
    qsort(nums, numsSize, sizeof(int), cmp);
    return nums[k - 1];
}
```

---

### 9. LC 11 - Container With Most Water (Medium)
**Link:** https://leetcode.com/problems/container-with-most-water/  
```c
int maxArea(int* height, int heightSize) {
    int left = 0, right = heightSize - 1;
    int max_water = 0;
    while (left < right) {
        int h = height[left] < height[right] ? height[left] : height[right];
        int w = right - left;
        int area = h * w;
        if (area > max_water) max_water = area;
        if (height[left] < height[right]) left++;
        else right--;
    }
    return max_water;
}
```

---

### 10. LC 15 - 3Sum (Medium)
**Link:** https://leetcode.com/problems/3sum/  
```c
int cmp_int(const void* a, const void* b) {
    return (*(int*)a - *(int*)b);
}

int** threeSum(int* nums, int numsSize, int* returnSize, int** returnColumnSizes) {
    qsort(nums, numsSize, sizeof(int), cmp_int);
    int capacity = 2000;
    int** res = (int**)malloc(sizeof(int*) * capacity);
    *returnColumnSizes = (int*)malloc(sizeof(int) * capacity);
    *returnSize = 0;

    for (int i = 0; i < numsSize - 2; i++) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        int left = i + 1, right = numsSize - 1;
        while (left < right) {
            int sum = nums[i] + nums[left] + nums[right];
            if (sum == 0) {
                if (*returnSize >= capacity) {
                    capacity *= 2;
                    res = (int**)realloc(res, sizeof(int*) * capacity);
                    *returnColumnSizes = (int*)realloc(*returnColumnSizes, sizeof(int) * capacity);
                }
                res[*returnSize] = (int*)malloc(sizeof(int) * 3);
                res[*returnSize][0] = nums[i];
                res[*returnSize][1] = nums[left];
                res[*returnSize][2] = nums[right];
                (*returnColumnSizes)[*returnSize] = 3;
                (*returnSize)++;
                
                while (left < right && nums[left] == nums[left + 1]) left++;
                while (left < right && nums[right] == nums[right - 1]) right--;
                left++; right--;
            } else if (sum < 0) {
                left++;
            } else {
                right--;
            }
        }
    }
    return res;
}
```

---

### 11. LC 56 - Merge Intervals (Medium)
**Link:** https://leetcode.com/problems/merge-intervals/  
```c
int cmp_intervals(const void* a, const void* b) {
    int* ia = *(int**)a;
    int* ib = *(int**)b;
    return ia[0] - ib[0];
}

int** merge(int** intervals, int intervalsSize, int* intervalsColSize, int* returnSize, int** returnColumnSizes) {
    if (intervalsSize <= 0) {
        *returnSize = 0;
        return NULL;
    }
    qsort(intervals, intervalsSize, sizeof(int*), cmp_intervals);
    int** res = (int**)malloc(sizeof(int*) * intervalsSize);
    *returnColumnSizes = (int*)malloc(sizeof(int) * intervalsSize);
    
    int count = 0;
    res[0] = (int*)malloc(sizeof(int) * 2);
    res[0][0] = intervals[0][0];
    res[0][1] = intervals[0][1];
    (*returnColumnSizes)[0] = 2;
    count = 1;

    for (int i = 1; i < intervalsSize; i++) {
        if (intervals[i][0] <= res[count - 1][1]) {
            if (intervals[i][1] > res[count - 1][1])
                res[count - 1][1] = intervals[i][1];
        } else {
            res[count] = (int*)malloc(sizeof(int) * 2);
            res[count][0] = intervals[i][0];
            res[count][1] = intervals[i][1];
            (*returnColumnSizes)[count] = 2;
            count++;
        }
    }
    *returnSize = count;
    return res;
}
```

---

### 12. LC 2 - Add Two Numbers (Medium)
**Link:** https://leetcode.com/problems/add-two-numbers/  
```c
struct ListNode* addTwoNumbers(struct ListNode* l1, struct ListNode* l2) {
    struct ListNode dummy;
    dummy.next = NULL;
    struct ListNode* curr = &dummy;
    int carry = 0;

    while (l1 || l2 || carry) {
        int sum = carry;
        if (l1) { sum += l1->val; l1 = l1->next; }
        if (l2) { sum += l2->val; l2 = l2->next; }
        carry = sum / 10;
        
        struct ListNode* node = (struct ListNode*)malloc(sizeof(struct ListNode));
        node->val = sum % 10;
        node->next = NULL;
        curr->next = node;
        curr = node;
    }
    return dummy.next;
}
```

---

### 13. LC 19 - Remove Nth Node From End of List (Medium)
**Link:** https://leetcode.com/problems/remove-nth-node-from-end-of-list/  
```c
struct ListNode* removeNthFromEnd(struct ListNode* head, int n) {
    struct ListNode dummy;
    dummy.val = 0;
    dummy.next = head;
    struct ListNode* fast = &dummy;
    struct ListNode* slow = &dummy;

    for (int i = 0; i <= n; i++) {
        fast = fast->next;
    }
    while (fast != NULL) {
        fast = fast->next;
        slow = slow->next;
    }
    struct ListNode* to_delete = slow->next;
    slow->next = slow->next->next;
    free(to_delete);
    return dummy.next;
}
```

---

### 14. LC 24 - Swap Nodes in Pairs (Medium)
**Link:** https://leetcode.com/problems/swap-nodes-in-pairs/  
```c
struct ListNode* swapPairs(struct ListNode* head) {
    if (!head || !head->next) return head;
    struct ListNode* second = head->next;
    head->next = swapPairs(second->next);
    second->next = head;
    return second;
}
```

---

### 15. LC 61 - Rotate List (Medium)
**Link:** https://leetcode.com/problems/rotate-list/  
```c
struct ListNode* rotateRight(struct ListNode* head, int k) {
    if (!head || !head->next || k == 0) return head;
    
    int len = 1;
    struct ListNode* tail = head;
    while (tail->next) {
        tail = tail->next;
        len++;
    }
    
    k %= len;
    if (k == 0) return head;
    
    tail->next = head; // Make circular
    int steps = len - k;
    struct ListNode* new_tail = tail;
    while (steps--) {
        new_tail = new_tail->next;
    }
    struct ListNode* new_head = new_tail->next;
    new_tail->next = NULL;
    return new_head;
}
```

---

### 16. LC 82 - Remove Duplicates from Sorted List II (Medium)
**Link:** https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/  
```c
struct ListNode* deleteDuplicates(struct ListNode* head) {
    struct ListNode dummy;
    dummy.next = head;
    struct ListNode* prev = &dummy;

    while (head) {
        if (head->next && head->val == head->next->val) {
            while (head->next && head->val == head->next->val) {
                head = head->next;
            }
            prev->next = head->next;
        } else {
            prev = prev->next;
        }
        head = head->next;
    }
    return dummy.next;
}
```

---

### 17. LC 86 - Partition List (Medium)
**Link:** https://leetcode.com/problems/partition-list/  
```c
struct ListNode* partition(struct ListNode* head, int x) {
    struct ListNode small_dummy, great_dummy;
    struct ListNode* small = &small_dummy;
    struct ListNode* great = &great_dummy;
    small->next = NULL;
    great->next = NULL;

    while (head) {
        if (head->val < x) {
            small->next = head;
            small = small->next;
        } else {
            great->next = head;
            great = great->next;
        }
        head = head->next;
    }
    great->next = NULL;
    small->next = great_dummy.next;
    return small_dummy.next;
}
```

---

### 18. LC 92 - Reverse Linked List II (Medium)
**Link:** https://leetcode.com/problems/reverse-linked-list-ii/  
```c
struct ListNode* reverseBetween(struct ListNode* head, int left, int right) {
    if (!head || left == right) return head;
    struct ListNode dummy;
    dummy.next = head;
    struct ListNode* prev = &dummy;

    for (int i = 1; i < left; i++) {
        prev = prev->next;
    }
    struct ListNode* curr = prev->next;
    for (int i = 0; i < right - left; i++) {
        struct ListNode* temp = curr->next;
        curr->next = temp->next;
        temp->next = prev->next;
        prev->next = temp;
    }
    return dummy.next;
}
```

---

### 19. LC 142 - Linked List Cycle II (Medium)
**Link:** https://leetcode.com/problems/linked-list-cycle-ii/  
```c
struct ListNode *detectCycle(struct ListNode *head) {
    if (!head || !head->next) return NULL;
    struct ListNode* slow = head;
    struct ListNode* fast = head;

    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) {
            struct ListNode* ptr1 = head;
            struct ListNode* ptr2 = slow;
            while (ptr1 != ptr2) {
                ptr1 = ptr1->next;
                ptr2 = ptr2->next;
            }
            return ptr1;
        }
    }
    return NULL;
}
```

---

### 20. LC 148 - Sort List (Medium)
**Link:** https://leetcode.com/problems/sort-list/  
```c
struct ListNode* mergeTwoLists(struct ListNode* l1, struct ListNode* l2) {
    struct ListNode dummy;
    struct ListNode* curr = &dummy;
    dummy.next = NULL;
    while (l1 && l2) {
        if (l1->val < l2->val) { curr->next = l1; l1 = l1->next; }
        else { curr->next = l2; l2 = l2->next; }
        curr = curr->next;
    }
    curr->next = l1 ? l1 : l2;
    return dummy.next;
}

struct ListNode* sortList(struct ListNode* head) {
    if (!head || !head->next) return head;
    struct ListNode* slow = head;
    struct ListNode* fast = head->next;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    struct ListNode* mid = slow->next;
    slow->next = NULL;
    return mergeTwoLists(sortList(head), sortList(mid));
}
```

---

### 21. LC 143 - Reorder List (Medium)
**Link:** https://leetcode.com/problems/reorder-list/  
```c
void reorderList(struct ListNode* head) {
    if (!head || !head->next) return;
    
    // 1. Find middle
    struct ListNode* slow = head;
    struct ListNode* fast = head;
    while (fast->next && fast->next->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    
    // 2. Reverse second half
    struct ListNode* prev = NULL;
    struct ListNode* curr = slow->next;
    slow->next = NULL;
    while (curr) {
        struct ListNode* nxt = curr->next;
        curr->next = prev;
        prev = curr;
        curr = nxt;
    }
    
    // 3. Merge two halves
    struct ListNode* first = head;
    struct ListNode* second = prev;
    while (second) {
        struct ListNode* t1 = first->next;
        struct ListNode* t2 = second->next;
        first->next = second;
        second->next = t1;
        first = t1;
        second = t2;
    }
}
```

---

### 22. LC 23 - Merge k Sorted Lists (Hard) 🏆
**Link:** https://leetcode.com/problems/merge-k-sorted-lists/  
```c
struct ListNode* merge2(struct ListNode* l1, struct ListNode* l2) {
    struct ListNode dummy;
    struct ListNode* curr = &dummy;
    dummy.next = NULL;
    while (l1 && l2) {
        if (l1->val < l2->val) { curr->next = l1; l1 = l1->next; }
        else { curr->next = l2; l2 = l2->next; }
        curr = curr->next;
    }
    curr->next = l1 ? l1 : l2;
    return dummy.next;
}

struct ListNode* mergeRange(struct ListNode** lists, int left, int right) {
    if (left > right) return NULL;
    if (left == right) return lists[left];
    int mid = left + (right - left) / 2;
    struct ListNode* l1 = mergeRange(lists, left, mid);
    struct ListNode* l2 = mergeRange(lists, mid + 1, right);
    return merge2(l1, l2);
}

struct ListNode* mergeKLists(struct ListNode** lists, int listsSize) {
    if (listsSize == 0) return NULL;
    return mergeRange(lists, 0, listsSize - 1);
}
```
