# AVL Tree Rotations and Balancing Mechanics

## Mathematical Foundations
An AVL (Adelson-Velsky and Landis) tree is a self-balancing binary search tree. The mathematical foundation of its balance is the **Balance Factor (BF)**.
- **BF(Node)** = `Height(Left Subtree) - Height(Right Subtree)`
- For any node in an AVL tree, the balance factor must strictly be `-1`, `0`, or `1`.
- If the BF becomes `<-1` or `>1` after an insertion or deletion, the tree is rebalanced through rotations.

## Algorithmic Time & Space Complexities
- **Time Complexity:** Search, Insertion, and Deletion are all guaranteed `O(log N)` because the tree's height is strictly bounded by `log N`.
- **Space Complexity:** `O(N)` for storing `N` nodes.

## The Four Rotations
When balancing is violated, one of four rotations is applied based on the insertion pattern:
1. **Left-Left (LL) Case (Right Rotation):** Node inserted into the left subtree of the left child.
2. **Right-Right (RR) Case (Left Rotation):** Node inserted into the right subtree of the right child.
3. **Left-Right (LR) Case (Left-Right Rotation):** Node inserted into the right subtree of the left child. (Requires Left rotation on child, then Right rotation on parent).
4. **Right-Left (RL) Case (Right-Left Rotation):** Node inserted into the left subtree of the right child. (Requires Right rotation on child, then Left rotation on parent).

## Clean Code Implementation (Python)

```python
class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def get_height(self, node):
        if not node:
            return 0
        return node.height

    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def right_rotate(self, y):
        x = y.left
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))

        return x

    def left_rotate(self, x):
        y = x.right
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    def insert(self, root, key):
        # 1. Perform standard BST insert
        if not root:
            return Node(key)
        elif key < root.key:
            root.left = self.insert(root.left, key)
        else:
            root.right = self.insert(root.right, key)

        # 2. Update the height of the ancestor node
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        # 3. Get the balance factor
        balance = self.get_balance(root)

        # 4. If unbalanced, balance the tree using the 4 cases

        # Case 1: Left Left
        if balance > 1 and key < root.left.key:
            return self.right_rotate(root)

        # Case 2: Right Right
        if balance < -1 and key > root.right.key:
            return self.left_rotate(root)

        # Case 3: Left Right
        if balance > 1 and key > root.left.key:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)

        # Case 4: Right Left
        if balance < -1 and key < root.right.key:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root
```
