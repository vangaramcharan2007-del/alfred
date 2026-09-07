"""
Autonomous Unit 3 Solver & Document Engine for SRM eCurricula (21CSC201J - DSA).
Generates full DOCX worksheets for RAM CHARAN VANGA (RA2511027010164) and converts them to PDF using ReportLab.
Covers all 14 Sessions (301 to 314), SLO 1 and SLO 2 (28 total files).
"""

import os
import sys
import html
from pathlib import Path
import docx
from docx.shared import Pt, Inches
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

STUDENT_NAME = "RAM CHARAN VANGA"
REG_NO = "RA2511027010164"
SUBJECT = "Sub ject : DSA"

OUT_DIR = Path("outputs/srm_unit3_solved")
DOCX_DIR = OUT_DIR / "docx"
PDF_DIR = OUT_DIR / "pdfs"

DOCX_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

SOLUTIONS = {
    # Session 1 (301)
    "U3S1SLO1": (1, 1, "Stacks Introduction", [
        ("1. A stack is a ____ data structure.", "linear (LIFO - Last In First Out)"),
        ("2. The two main operations of a stack are ____ and ____.", "push and pop"),
        ("3. The operation that adds an element to a stack is called ____.", "push"),
        ("4. The operation that removes the top element from the stack is called ____.", "pop"),
        ("5. The operation that returns the top element without removing it is called ____.", "peek (or top)"),
        ("6. If a stack is full and a push operation is attempted, it is called ____.", "stack overflow"),
        ("7. If a stack is empty and a pop operation is attempted, it is called ____.", "stack underflow"),
        ("8. Stacks are usually implemented using ____ or ____.", "arrays or linked lists"),
        ("9. In array implementation of stack, the top element is accessed using the ____ index.", "TOP"),
        ("10. In function calls, the system uses a stack to store ____.", "activation records (return addresses, local variables, and parameters)"),
        ("11. The initial value of top in an empty stack array implementation is usually ____.", "-1"),
        ("12. Stack is used in ____ notation to evaluate expressions without parentheses.", "postfix (Reverse Polish) / prefix"),
        ("13. A stack is also used in ____ traversal of trees.", "depth-first (preorder, inorder, postorder)"),
        ("14. The time complexity of push and pop operations in a stack is ____.", "O(1) (constant time)"),
        ("15. Reversing a string using stack works by ____ each character and then ____ them.", "pushing each character and then popping them")
    ]),

    "U3S1SLO2": (1, 2, "Stack Implementation Using Array", [
        ("Push Operation - Algorithm to insert an element in a stack\nStep 1: IF TOP = MAX-1\n  PRINT _____________\nGoto Step 4\n[END OF IF]\nStep 2: SET TOP = ___________\nStep 3: SET STACK[______] = VALUE\nStep 4: END",
         "Step 1: PRINT OVERFLOW\nStep 2: SET TOP = TOP + 1\nStep 3: SET STACK[TOP] = VALUE\nStep 4: END"),
        ("Pop Operation - Algorithm to delete an element from a stack\nStep 1: IF TOP = _____\nPRINT UNDERFLOW\nGoto Step 4\n[END OF IF]\nStep 2: SET VAL = STACK[______]\nStep 3: SET TOP = _________\nStep 4: END",
         "Step 1: IF TOP = -1\nStep 2: SET VAL = STACK[TOP]\nStep 3: SET TOP = TOP - 1\nStep 4: END"),
        ("Peek Operation - Algorithm for Peek operation\nStep 1: IF TOP = _______\nPRINT STACK IS EMPTY\nGoto Step 3\n[END OF IF]\nStep 2: RETURN STACK[_______]\nStep 3: END",
         "Step 1: IF TOP = -1\nStep 2: RETURN STACK[TOP]\nStep 3: END")
    ]),

    # Session 2 (302)
    "U3S2SLO1": (2, 1, "Stack Implementation Using Array - Advantages, Disadvantages and Applications", [
        ("1. Stack implementation using arrays is ____ to implement.", "easy / simple"),
        ("2. Accessing elements in an array is ____ due to direct indexing.", "fast (constant time O(1))"),
        ("3. Stack operations like push and pop take ____ time in array implementation.", "O(1) constant"),
        ("4. Arrays provide ____ memory allocation at compile time.", "static"),
        ("5. Array-based stacks have ____ memory access, improving performance.", "contiguous / cache-friendly"),
        ("6. There is no overhead of memory allocation and ____ in arrays.", "deallocation (pointer overhead)"),
        ("7. Array-based stack implementation avoids the extra memory used for ____ in linked lists.", "pointers (next address fields)"),
        ("8. It is easier to ____ a stack implemented using arrays in programming.", "debug and visualize"),
        ("9. Array implementation of stack is ____ in terms of memory for small, fixed-size stacks.", "efficient"),
        ("10. Stack overflow in array implementation is ____ to detect.", "straightforward / easy (check TOP == MAX-1)"),
        ("11. Stack implemented using arrays has a fixed ____ size.", "maximum capacity"),
        ("12. If the stack size is too small, it may lead to ____.", "stack overflow"),
        ("13. If the stack size is too large, it may lead to ____ of memory.", "wastage (unused allocated space)"),
        ("14. Arrays use ____ memory allocation, which is less flexible.", "static"),
        ("15. It is difficult to ____ the size of a stack implemented using arrays at runtime.", "resize / dynamically change"),
        ("16. Stack operations using arrays are not memory ____ for large data.", "flexible / dynamic"),
        ("17. Inserting or removing elements from the stack may require checking for ____ or underflow.", "overflow"),
        ("18. Reallocation of array memory is ____ and not always supported in some languages.", "costly (O(n) copying)"),
        ("19. Array implementation is not suitable when the maximum stack size is ____.", "unknown or unpredictable"),
        ("20. Stack implemented using arrays may not efficiently use ____ in dynamic scenarios.", "memory resources"),
        ("21. Stacks are used in ____ evaluation and conversion.", "expression (infix, postfix, prefix)")
    ]),

    "U3S2SLO2": (2, 2, "Stack Implementation Using Linked Lists", [
        ("Push Operation - Algorithm to insert an element VAL in a linked stack\nStep 1: Allocate memory for the new node and name it as NEW_NODE\nStep 2: SET NEW_NODE -> DATA = VAL\nStep 3: IF TOP = NULL\n  SET NEW_NODE -> NEXT = NULL\n  SET TOP = NEW_NODE\nELSE\n  SET NEW_NODE -> NEXT = _________\n  SET TOP = ____________\n[END OF IF]\nStep 4: END",
         "Step 3: SET NEW_NODE -> NEXT = TOP\nSET TOP = NEW_NODE\nStep 4: END"),
        ("Pop Operation - Algorithm to delete an element from a linked stack\nStep 1: IF TOP = NULL\n  PRINT UNDERFLOW\n  Goto Step 5\n[END OF IF]\nStep 2: SET PTR = TOP\nStep 3: SET TOP = TOP -> _________\nStep 4: FREE _________\nStep 5: END",
         "Step 3: SET TOP = TOP -> NEXT\nStep 4: FREE PTR\nStep 5: END"),
        ("Peek Operation - Algorithm for peek in linked stack\nStep 1: IF TOP = NULL\n  PRINT STACK IS EMPTY\n  Goto Step 3\n[END OF IF]\nStep 2: RETURN TOP -> _________\nStep 3: END",
         "Step 2: RETURN TOP -> DATA\nStep 3: END")
    ]),

    # Session 3 (303)
    "U3S3SLO1": (3, 1, "Stack Implementation Using Linked Lists - Advantages, Disadvantages and Applications", [
        ("1. In pointer-based stacks, memory is allocated ____.", "dynamically at runtime"),
        ("2. In pointer-based stacks, there is no need to define the ____ stack size.", "fixed maximum"),
        ("3. Stack implemented using pointers can easily grow and ____ at runtime.", "shrink"),
        ("4. There is no ____ of memory since space is allocated as needed.", "wastage"),
        ("5. Linked list-based stacks can handle a large number of elements until the system runs out of ____.", "heap memory"),
        ("6. Pointer-based stack avoids ____ overflow, unlike array-based stacks.", "stack"),
        ("7. In pointer-based implementation, memory is released using ____ when elements are popped.", "free() / deallocation"),
        ("8. Stacks using pointers are more ____ for programs requiring flexible memory use.", "adaptable / dynamic"),
        ("9. No need to ____ the stack when it becomes full, unlike arrays.", "reallocate or resize"),
        ("10. Each node in a linked list-based stack contains both data and a ____ to the next node.", "pointer (next)"),
        ("11. Stack implementation using pointers requires extra memory for storing ____.", "pointers (addresses)"),
        ("12. Each node in a linked list-based stack uses more ____ than array-based stacks.", "memory space"),
        ("13. Accessing elements in a pointer-based stack is ____ than in an array.", "slower (due to pointer dereferencing)"),
        ("14. Stack operations in linked lists involve dynamic memory allocation, which can be ____.", "time-consuming (overhead)"),
        ("15. Improper memory management in pointer-based stacks can lead to ____ leaks.", "memory"),
        ("16. Debugging a pointer-based stack is more ____ than an array-based stack.", "complex"),
        ("17. Pointer-based stack implementation depends on ____ allocation at runtime.", "dynamic heap"),
        ("18. Excessive use of pointers increases the risk of ____ errors.", "segmentation fault / dangling pointer"),
        ("19. It is harder to determine the total number of elements without ____ through the stack.", "traversing"),
        ("20. Stack operations in pointer-based implementation are not as ____ as array-based stacks for small data sets.", "cache efficient"),
        ("21. Stack using pointers is useful in handling ____ size data efficiently.", "variable / dynamic"),
        ("22. Function call management in recursion uses a ____ stack.", "call / execution"),
        ("23. Pointer-based stacks are suitable for evaluating and converting ____ expressions.", "arithmetic (infix/postfix/prefix)"),
        ("24. Stacks help in implementing ____ and redo features in applications.", "undo"),
        ("25. Pointer-based stacks are used in ____ parsing for compilers.", "syntax / expression"),
        ("26. Backtracking algorithms like maze solving or N-Queens use ____.", "stacks"),
        ("27. Stack using pointers is helpful in managing ____ frames in programming languages.", "stack / activation"),
        ("28. Depth-first search (DFS) in graphs can be implemented using a ____.", "stack"),
        ("29. Stacks are used in checking ____ of parentheses in expressions.", "balance / validity"),
        ("30. Linked list-based stacks are useful in systems with limited or unpredictable ____ availability.", "memory")
    ]),

    "U3S3SLO2": (3, 2, "Stack Applications - Matching", [
        ("Match the Stack Applications with their corresponding functional description:\nA. Expression Evaluation\nB. Reverse Characters\nC. Syntax Parsing\nD. Backtracking\nE. Undo Mechanism\nF. Function Call Management\nG. Parenthesis Checking\nH. Browser History\nI. Reversing a String\nJ. Tower of Hanoi",
         "A - 8 (Converts infix to postfix or prefix and evaluates expressions)\n"
         "B - 3 (Characters are popped in reverse order)\n"
         "C - 9 (Helps in checking for balanced symbols / grammar verification)\n"
         "D - 6 (Used in solving mazes or puzzles via recursive exploration)\n"
         "E - 7 (Maintains previous states of user actions for rollbacks)\n"
         "F - 4 (Uses call stack to manage function activation records)\n"
         "G - 5 (Verifies matching of open and close brackets)\n"
         "H - 1 (Navigates forward and backward between visited web pages)\n"
         "I - 10 (Uses stack LIFO property to reverse sequence of characters)\n"
         "J - 2 (Uses recursion implemented via call stack to transfer disks)")
    ]),

    # Session 4 (304)
    "U3S4SLO1": (4, 1, "Stack Applications - Reversing a List and Balancing Symbols", [
        ("1. Consider any 5 elements in a List in an array A = [10, 20, 30, 40, 50]. Use a Stack S using array implementation and Reverse the Elements of the List into array B.\nStep 1: Representation of elements in the List\nStep 2: Traverse list from first element and push into Stack S\nStep 3: Pop elements one by one from TOP and place in array B",
         "Step 1: Array A = [10, 20, 30, 40, 50], N = 5.\n"
         "Step 2: Traverse A from index 0 to 4 and push each element onto Stack S:\n"
         "  - push(10) -> S: [10] (TOP=0)\n"
         "  - push(20) -> S: [10, 20] (TOP=1)\n"
         "  - push(30) -> S: [10, 20, 30] (TOP=2)\n"
         "  - push(40) -> S: [10, 20, 30, 40] (TOP=3)\n"
         "  - push(50) -> S: [10, 20, 30, 40, 50] (TOP=4)\n"
         "Step 3: Pop elements from Stack S and place into array B:\n"
         "  - pop() -> 50, B[0] = 50\n"
         "  - pop() -> 40, B[1] = 40\n"
         "  - pop() -> 30, B[2] = 30\n"
         "  - pop() -> 20, B[3] = 20\n"
         "  - pop() -> 10, B[4] = 10\n"
         "Result: Array B = [50, 40, 30, 20, 10] (Successfully Reversed!)"),
        ("2. Check if the following expressions have balanced parenthesis using stack:\na. { P + ( Q - R ) }\nb. { D * ( S + A) )",
         "a. Expression: { P + ( Q - R ) }\n"
         "  Step 1: Initialize flag = 1, Stack S = empty\n"
         "  Step 2: Scan '{' -> Push '{' onto stack S -> S = ['{']\n"
         "  Step 3: Scan 'P', '+' -> Operands/operators ignored\n"
         "  Step 4: Scan '(' -> Push '(' onto stack S -> S = ['{', '(']\n"
         "  Step 5: Scan 'Q', '-', 'R' -> Ignored\n"
         "  Step 6: Scan ')' -> Pop from S -> popped '(' matches ')' -> S = ['{']\n"
         "  Step 7: Scan '}' -> Pop from S -> popped '{' matches '}' -> S = empty\n"
         "  Step 8: End of expression. Stack is empty and flag = 1 -> VALID (Balanced Parentheses)\n\n"
         "b. Expression: { D * ( S + A) )\n"
         "  Step 1: Initialize flag = 1, Stack S = empty\n"
         "  Step 2: Scan '{' -> Push '{' -> S = ['{']\n"
         "  Step 3: Scan '(' -> Push '(' -> S = ['{', '(']\n"
         "  Step 4: Scan ')' -> Pop '(' -> S = ['{']\n"
         "  Step 5: Scan ')' -> Pop '{' -> Mismatched opening bracket ('{' does not match ')') -> flag = 0\n"
         "  Step 6: End of expression. flag = 0 -> INVALID (Unbalanced Parentheses)")
    ]),

    "U3S4SLO2": (4, 2, "Stack Applications - Infix to Postfix Conversion 1", [
        ("Write an algorithm for Conversion of Infix Expression to Postfix using Stack.",
         "Algorithm InfixToPostfix(exp):\n"
         "Step 1: Push '(' onto Stack, and add ')' to the end of the infix expression exp.\n"
         "Step 2: Scan the infix expression exp from left to right until the Stack is empty.\n"
         "Step 3: For each scanned character C:\n"
         "  a. If C is an operand (alphanumeric), append C to the Postfix output string.\n"
         "  b. If C is '(', push C onto the Stack.\n"
         "  c. If C is an operator (+, -, *, /, ^, %):\n"
         "     i. While top of Stack has an operator of higher or equal precedence (or right-associative rules apply):\n"
         "        Pop the operator from Stack and append to Postfix output.\n"
         "     ii. Push C onto the Stack.\n"
         "  d. If C is ')':\n"
         "     i. Repeatedly pop from Stack and append to Postfix output until a '(' is encountered.\n"
         "     ii. Pop and discard the '(' from the Stack.\n"
         "Step 4: Return Postfix output expression.\n"
         "Step 5: Exit.")
    ]),

    # Session 5 (305)
    "U3S5SLO1": (5, 1, "Stack Applications - Infix to Postfix Conversion 2", [
        ("Convert the following infix expression into postfix expression using the algorithm using stacks:\nA – (B / C + (D % E * F) / G)* H",
         "Conversion Trace:\n"
         "Initial Stack: [ ( ], Append ')' to expression.\n"
         "1. Scan 'A': Operand -> Postfix: A\n"
         "2. Scan '-': Operator -> Stack: [ (, - ]\n"
         "3. Scan '(': Left Paren -> Stack: [ (, -, ( ]\n"
         "4. Scan 'B': Operand -> Postfix: A B\n"
         "5. Scan '/': Operator -> Stack: [ (, -, (, / ]\n"
         "6. Scan 'C': Operand -> Postfix: A B C\n"
         "7. Scan '+': Lower precedence than '/' -> Pop '/' -> Postfix: A B C / -> Push '+' -> Stack: [ (, -, (, + ]\n"
         "8. Scan '(': Left Paren -> Stack: [ (, -, (, +, ( ]\n"
         "9. Scan 'D': Operand -> Postfix: A B C / D\n"
         "10. Scan '%': Operator -> Stack: [ (, -, (, +, (, % ]\n"
         "11. Scan 'E': Operand -> Postfix: A B C / D E\n"
         "12. Scan '*': Same precedence as '%' (left-assoc) -> Pop '%' -> Postfix: A B C / D E % -> Push '*' -> Stack: [ (, -, (, +, (, * ]\n"
         "13. Scan 'F': Operand -> Postfix: A B C / D E % F\n"
         "14. Scan ')': Pop '*' -> Postfix: A B C / D E % F * -> Pop '(' -> Stack: [ (, -, (, + ]\n"
         "15. Scan '/': Higher precedence than '+' -> Push '/' -> Stack: [ (, -, (, +, / ]\n"
         "16. Scan 'G': Operand -> Postfix: A B C / D E % F * G\n"
         "17. Scan ')': Pop '/' -> Postfix: ... G / -> Pop '+' -> Postfix: ... G / + -> Pop '(' -> Stack: [ (, - ]\n"
         "18. Scan '*': Higher precedence than '-' -> Push '*' -> Stack: [ (, -, * ]\n"
         "19. Scan 'H': Operand -> Postfix: A B C / D E % F * G / + H\n"
         "20. Scan end ')': Pop '*' -> Postfix: ... H * -> Pop '-' -> Postfix: ... H * - -> Pop '(' -> Stack empty.\n\n"
         "Final Postfix Expression: A B C / D E % F * G / + H * -")
    ]),

    "U3S5SLO2": (5, 2, "Stack Applications - Evaluating Postfix Expression", [
        ("Algorithm to evaluate a postfix expression",
         "Algorithm EvaluatePostfix(exp):\n"
         "Step 1: Create an empty Stack.\n"
         "Step 2: Scan the Postfix expression from left to right token by token.\n"
         "Step 3: For each scanned element X:\n"
         "  a. If X is an operand (number), push X onto the Stack.\n"
         "  b. If X is an operator (such as +, -, *, /, %):\n"
         "     i. Pop operand2 from Stack: operand2 = pop()\n"
         "     ii. Pop operand1 from Stack: operand1 = pop()\n"
         "     iii. Compute result = operand1 (operator) operand2\n"
         "     iv. Push result back onto the Stack.\n"
         "Step 4: When the expression ends, the final result is the only value remaining on the Stack: return pop().\n"
         "Step 5: Exit."),
        ("Follow the Algorithm and Solve: Evaluation of a postfix expression\n9 3 4 * 8 + 4 / -",
         "Step-by-step Evaluation Trace:\n"
         "1. Scan '9': Operand -> Push 9 -> Stack: [9]\n"
         "2. Scan '3': Operand -> Push 3 -> Stack: [9, 3]\n"
         "3. Scan '4': Operand -> Push 4 -> Stack: [9, 3, 4]\n"
         "4. Scan '*': Operator -> Pop 4, Pop 3 -> Compute 3 * 4 = 12 -> Push 12 -> Stack: [9, 12]\n"
         "5. Scan '8': Operand -> Push 8 -> Stack: [9, 12, 8]\n"
         "6. Scan '+': Operator -> Pop 8, Pop 12 -> Compute 12 + 8 = 20 -> Push 20 -> Stack: [9, 20]\n"
         "7. Scan '4': Operand -> Push 4 -> Stack: [9, 20, 4]\n"
         "8. Scan '/': Operator -> Pop 4, Pop 20 -> Compute 20 / 4 = 5 -> Push 5 -> Stack: [9, 5]\n"
         "9. Scan '-': Operator -> Pop 5, Pop 9 -> Compute 9 - 5 = 4 -> Push 4 -> Stack: [4]\n"
         "End of expression reached.\n\n"
         "Final Evaluated Result = 4")
    ]),

    # Session 6 (306)
    "U3S6SLO1": (6, 1, "Stack Applications - Recursion", [
        ("1. In recursion, each function call is stored in the ____.", "call stack (system stack)"),
        ("2. The ____ principle is followed by stacks.", "LIFO (Last In, First Out)"),
        ("3. Stack is used internally to implement ____ function calls.", "recursive"),
        ("4. Every recursive function must have a ____ condition to avoid infinite calls.", "base"),
        ("5. The process of returning from a recursive function happens in the ____ order of calls.", "reverse"),
        ("6. Each recursive call adds a new ____ to the stack.", "activation record (stack frame)"),
        ("7. ____ is a classic example of a problem solved using recursion and stacks.", "Factorial / Tower of Hanoi / Fibonacci"),
        ("8. The return address and local variables are stored in the function’s ____.", "stack frame"),
        ("9. The system stack helps in managing ____ function calls during recursion.", "nested"),
        ("10. When the base case is reached, the stack starts to ____.", "unwind (pop frames)")
    ]),

    "U3S6SLO2": (6, 2, "Stack Applications - Tower of Hanoi", [
        ("1. ____ is a classic problem that demonstrates the use of recursion with stacks.", "Tower of Hanoi"),
        ("2. The minimum number of moves required to solve the Towers of Hanoi with n disks is ____.", "2^n - 1"),
        ("3. The recursive solution to Towers of Hanoi uses the ____ data structure to manage function calls.", "call stack"),
        ("4. In the Towers of Hanoi, disks are moved from the source rod to the ____ rod using an auxiliary rod.", "destination (target)"),
        ("5. Each recursive call pushes a new ____ onto the stack.", "activation frame (state)"),
        ("6. The Towers of Hanoi involves ____ recursive steps.", "two (T(n-1) moves)"),
        ("7. The stack unwinds when the ____ case of the recursive function is reached.", "base (n == 1)"),
        ("8. The base condition in Towers of Hanoi is when ____ disk is to be moved.", "one (single)"),
        ("9. Stacks in recursion help to ____ the order of operations in solving the puzzle.", "track and restore"),
        ("10. The auxiliary rod in the Towers of Hanoi acts as a ____ during disk transfers.", "temporary buffer (helper)")
    ]),

    # Session 7 (307)
    "U3S7SLO1": (7, 1, "Implementation of Stack using Array", [
        ("Build the code for Implementation of Stacks using Array:\na. Declare the stack with size MAX, initialize 'top'\nb. Write a function push with arguments int st[ ] and int val\nc. Write a function pop with argument int st[ ]\nd. Write a function peek with argument int st[ ]",
         "/* a. Declaration and Initialization */\n"
         "#define MAX 100\n"
         "int st[MAX];\n"
         "int top = -1;\n\n"
         "/* b. Push Function */\n"
         "void push(int st[], int val) {\n"
         "    if (top == MAX - 1) {\n"
         "        printf(\"\nStack Overflow! Cannot push %d\\n\", val);\n"
         "        return;\n"
         "    }\n"
         "    top++;\n"
         "    st[top] = val;\n"
         "    printf(\"\nPushed %d to stack\\n\", val);\n"
         "}\n\n"
         "/* c. Pop Function */\n"
         "int pop(int st[]) {\n"
         "    if (top == -1) {\n"
         "        printf(\"\nStack Underflow! Stack is empty\\n\");\n"
         "        return -1;\n"
         "    }\n"
         "    int val = st[top];\n"
         "    top--;\n"
         "    return val;\n"
         "}\n\n"
         "/* d. Peek Function */\n"
         "int peek(int st[]) {\n"
         "    if (top == -1) {\n"
         "        printf(\"\nStack is Empty!\\n\");\n"
         "        return -1;\n"
         "    }\n"
         "    return st[top];\n"
         "}")
    ]),

    "U3S7SLO2": (7, 2, "Implementation of Stack using Linked List", [
        ("Build the code for Implementation of Stacks using Linked Lists (Pointer Implementation):\na. Define the structure for a node\nb. Write a function for push operation with arguments top and int val\nc. Write a function for pop operation with arguments top\nd. Write a function for peek operation with arguments top",
         "/* a. Node Structure Definition */\n"
         "struct node {\n"
         "    int data;\n"
         "    struct node *next;\n"
         "};\n\n"
         "/* b. Push Function */\n"
         "struct node *push(struct node *top, int val) {\n"
         "    struct node *new_node = (struct node *)malloc(sizeof(struct node));\n"
         "    if (new_node == NULL) {\n"
         "        printf(\"\nHeap Overflow! Unable to allocate memory\\n\");\n"
         "        return top;\n"
         "    }\n"
         "    new_node->data = val;\n"
         "    new_node->next = top;\n"
         "    top = new_node;\n"
         "    printf(\"\nPushed %d onto linked stack\\n\", val);\n"
         "    return top;\n"
         "}\n\n"
         "/* c. Pop Function */\n"
         "struct node *pop(struct node *top) {\n"
         "    if (top == NULL) {\n"
         "        printf(\"\nStack Underflow! Linked stack is empty\\n\");\n"
         "        return NULL;\n"
         "    }\n"
         "    struct node *ptr = top;\n"
         "    printf(\"\nPopped element: %d\\n\", ptr->data);\n"
         "    top = top->next;\n"
         "    free(ptr);\n"
         "    return top;\n"
         "}\n\n"
         "/* d. Peek Function */\n"
         "int peek(struct node *top) {\n"
         "    if (top == NULL) {\n"
         "        printf(\"\nStack is Empty!\\n\");\n"
         "        return -1;\n"
         "    }\n"
         "    return top->data;\n"
         "}")
    ]),

    # Session 8 (308)
    "U3S8SLO1": (8, 1, "Queue Introduction", [
        ("1. A queue follows the ____ principle.", "FIFO (First In, First Out)"),
        ("2. In a queue, insertion is performed at the ____ end.", "rear"),
        ("3. In a queue, deletion is performed at the ____ end.", "front"),
        ("4. A ____ queue is a linear data structure with a fixed size.", "linear (array-based)"),
        ("5. A ____ queue overcomes the limitation of fixed size by wrapping around.", "circular"),
        ("6. A ____ queue allows insertion and deletion from both ends.", "deque (double-ended)"),
        ("7. ____ queue gives priority to elements based on certain criteria.", "Priority"),
        ("8. Queues are used in ____ scheduling in operating systems.", "CPU / process / I/O"),
        ("9. In a queue, if the rear is just behind the front in a circular manner, the queue is said to be ____.", "full"),
        ("10. A ____ is used to implement queues in programming languages like C.", "array or linked list"),
        ("11. The queue operation that checks whether it is full is called ____.", "isFull()"),
        ("12. The queue operation that checks whether it is empty is called ____.", "isEmpty()"),
        ("13. In breadth-first search (BFS) of a graph, ____ is used to keep track of the next node to visit.", "a queue"),
        ("14. In printers, tasks are managed using a ____ to print in the order they arrive.", "print spooler / queue"),
        ("15. A queue where new elements are added based on priority rather than position is called a ____.", "priority queue")
    ]),

    "U3S8SLO2": (8, 2, "Queue Implementation Using Array", [
        ("Enqueue Operation - Algorithm to insert an element NUM in a queue\nStep 1: IF REAR = _____________\nWrite OVERFLOW\nGoto step 4\n[END OF IF]\nStep 2: IF FRONT=___ and REAR= _____\nSET FRONT = REAR = 0\nELSE\nSET REAR = __________\n[END OF IF]\nStep 3: SET QUEUE[REAR] = _______\nStep 4: EXIT",
         "Step 1: IF REAR = MAX - 1\nStep 2: IF FRONT = -1 and REAR = -1\n  SET FRONT = REAR = 0\n  ELSE\n  SET REAR = REAR + 1\nStep 3: SET QUEUE[REAR] = NUM\nStep 4: EXIT"),
        ("Dequeue Operation – Algorithm to delete an element from a queue\nStep 1: IF FRONT = _____ OR FRONT > __________\nWrite UNDERFLOW\nELSE\nSET VAL = ______________\nSET FRONT = ______________\n[END OF IF]\nStep 2: EXIT",
         "Step 1: IF FRONT = -1 OR FRONT > REAR\n  Write UNDERFLOW\n  ELSE\n  SET VAL = QUEUE[FRONT]\n  SET FRONT = FRONT + 1\nStep 2: EXIT")
    ]),

    # Session 9 (309)
    "U3S9SLO1": (9, 1, "Queue Implementation Using Linked List", [
        ("Enqueue Operation - Algorithm to insert an element VAL in a queue\nStep 1: Allocate memory for the new node and name it as PTR\nStep 2: SET PTR -> DATA = _________\nStep 3: IF FRONT = NULL\nSET FRONT = REAR = __________\nSET FRONT -> NEXT = REAR -> NEXT = ____________\nELSE\n SET ________________ = PTR\nSET __________ = PTR\nSET _____________ = NULL\n[END OF IF]\nStep 4: END",
         "Step 2: SET PTR -> DATA = VAL\n"
         "Step 3: IF FRONT = NULL\n"
         "  SET FRONT = REAR = PTR\n"
         "  SET FRONT -> NEXT = REAR -> NEXT = NULL\n"
         "  ELSE\n"
         "  SET REAR -> NEXT = PTR\n"
         "  SET REAR = PTR\n"
         "  SET REAR -> NEXT = NULL\n"
         "Step 4: END"),
        ("Dequeue Operation – Algorithm to delete an element from a queue\nStep 1: IF FRONT = NULL\n  Write ______________\nGo to Step 5\n[END OF IF]\nStep 2: SET PTR = _____________\nStep 3: SET FRONT = ________________\nStep 4: FREE _________\nStep 5: END",
         "Step 1: Write UNDERFLOW\n"
         "Step 2: SET PTR = FRONT\n"
         "Step 3: SET FRONT = FRONT -> NEXT\n"
         "Step 4: FREE PTR\n"
         "Step 5: END")
    ]),

    "U3S9SLO2": (9, 2, "Types of Queues - Matching", [
        ("Match the Types of Queues with their correct characteristic:\nA. Linear Queue\nB. Circular Queue\nC. Double-Ended Queue (Deque)\nD. Input-Restricted Deque\nE. Output-Restricted Deque\nF. Priority Queue\nG. Simple Queue\nH. Static Queue\nI. Dynamic Queue\nJ. Circular Deque\nK. Single-Ended Queue\nL. Blocking Queue\nM. Non-blocking Queue\nN. Monotonic Queue\nO. Queue of Queues",
         "A - 2 (Basic FIFO structure)\n"
         "B - 13 (Last position connects to the first, wrapping around)\n"
         "C - 11 (Insertion and deletion at both ends)\n"
         "D - 9 (Deletion at both ends, insertion at one end only)\n"
         "E - 12 (Insertion at both ends, deletion at one end only)\n"
         "F - 10 (Elements served based on importance/priority)\n"
         "G - 15 (Insertion at rear, deletion at front)\n"
         "H - 3 (Fixed size queue implemented using arrays)\n"
         "I - 1 (Grows or shrinks dynamically using linked list)\n"
         "J - 14 (Ends are connected circularly and operations at both ends)\n"
         "K - 8 (Operation allowed at only designated ends)\n"
         "L - 5 (Used for thread communication, blocks on full/empty)\n"
         "M - 7 (Does not wait, returns status immediately)\n"
         "N - 6 (Maintains elements in increasing or decreasing order)\n"
         "O - 4 (Nested queue structure with queues as elements)")
    ]),

    # Session 10 (310)
    "U3S10SLO1": (10, 1, "Implementation of Queue using Array", [
        ("Build the code for Implementation of Queues using Array:\na. Declare the queue with size MAX, initialize 'front' and 'rear'\nb. Write a function enqueue to insert elements at the rear end\nc. Write a function dequeue to delete elements from the front of the queue",
         "/* a. Declaration and Initialization */\n"
         "#define MAX 100\n"
         "int queue[MAX];\n"
         "int front = -1, rear = -1;\n\n"
         "/* b. Enqueue Function */\n"
         "void enqueue(int val) {\n"
         "    if (rear == MAX - 1) {\n"
         "        printf(\"\nQueue Overflow! Cannot enqueue %d\\n\", val);\n"
         "        return;\n"
         "    }\n"
         "    if (front == -1 && rear == -1) {\n"
         "        front = rear = 0;\n"
         "    } else {\n"
         "        rear++;\n"
         "    }\n"
         "    queue[rear] = val;\n"
         "    printf(\"\nEnqueued: %d\\n\", val);\n"
         "}\n\n"
         "/* c. Dequeue Function */\n"
         "int dequeue() {\n"
         "    if (front == -1 || front > rear) {\n"
         "        printf(\"\nQueue Underflow! Queue is empty\\n\");\n"
         "        return -1;\n"
         "    }\n"
         "    int val = queue[front];\n"
         "    front++;\n"
         "    if (front > rear) {\n"
         "        front = rear = -1; // Reset queue\n"
         "    }\n"
         "    return val;\n"
         "}")
    ]),

    "U3S10SLO2": (10, 2, "Implementation of Queue using Linked List", [
        ("Build the code for Implementation of Queues using Linked List (Pointer Implementation):\na. Define the structure for a node\nb. Write a function for enqueue operation with arguments struct queue *q and int val\nc. Write a function for dequeue operation with arguments struct queue *q",
         "/* a. Node and Queue Structures */\n"
         "struct node {\n"
         "    int data;\n"
         "    struct node *next;\n"
         "};\n\n"
         "struct queue {\n"
         "    struct node *front;\n"
         "    struct node *rear;\n"
         "};\n\n"
         "/* b. Enqueue Function */\n"
         "void enqueue(struct queue *q, int val) {\n"
         "    struct node *ptr = (struct node *)malloc(sizeof(struct node));\n"
         "    if (ptr == NULL) {\n"
         "        printf(\"\nMemory Allocation Failed!\\n\");\n"
         "        return;\n"
         "    }\n"
         "    ptr->data = val;\n"
         "    ptr->next = NULL;\n"
         "    if (q->front == NULL) {\n"
         "        q->front = q->rear = ptr;\n"
         "    } else {\n"
         "        q->rear->next = ptr;\n"
         "        q->rear = ptr;\n"
         "    }\n"
         "    printf(\"\nEnqueued to linked queue: %d\\n\", val);\n"
         "}\n\n"
         "/* c. Dequeue Function */\n"
         "int dequeue(struct queue *q) {\n"
         "    if (q->front == NULL) {\n"
         "        printf(\"\nQueue Underflow! Linked queue is empty\\n\");\n"
         "        return -1;\n"
         "    }\n"
         "    struct node *ptr = q->front;\n"
         "    int val = ptr->data;\n"
         "    q->front = q->front->next;\n"
         "    if (q->front == NULL) {\n"
         "        q->rear = NULL;\n"
         "    }\n"
         "    free(ptr);\n"
         "    return val;\n"
         "}")
    ]),

    # Session 11 (311)
    "U3S11SLO1": (11, 1, "Circular Queue - Introduction", [
        ("1. A circular queue connects the ____ position back to the front.", "last (rear)"),
        ("2. Circular queue overcomes the problem of ____ in a linear queue.", "memory wastage (false overflow)"),
        ("3. In a circular queue, when the rear reaches the end, it wraps around to index ____.", "0 (zero)"),
        ("4. A circular queue follows the ____ principle.", "FIFO (First In, First Out)"),
        ("5. The condition for a full circular queue is: (rear + 1) % size == ____.", "front"),
        ("6. The condition for an empty circular queue is: front == ____.", "-1"),
        ("7. When the first element is inserted, both front and rear point to the ____ index.", "0th (first)"),
        ("8. Circular queues are commonly used in ____ scheduling.", "CPU round-robin / memory buffer"),
        ("9. The ____ function checks if a circular queue is full.", "isFull()"),
        ("10. The ____ function checks if a circular queue is empty.", "isEmpty()"),
        ("11. Circular queues help in utilizing memory more ____ than linear queues.", "efficiently"),
        ("12. In a circular queue, incrementing the rear is done using ____ operator.", "modulo (%)"),
        ("13. Circular queues can be implemented using arrays or ____.", "linked lists"),
        ("14. The front element of a circular queue is accessed using the ____ pointer.", "front"),
        ("15. In circular queues, rear and front move in a ____ manner.", "circular (clockwise)")
    ]),

    "U3S11SLO2": (11, 2, "Circular Queue - Enqueue Operation", [
        ("Algorithm to insert an element in a circular queue\nStep 1: IF FRONT = ____ and Rear = ____________\nWrite OVERFLOW\nGoto step 4\n[END OF IF]\nStep 2: IF FRONT=-1 and REAR=-1\nSET FRONT = REAR = _______\nELSE IF REAR = ____________ and FRONT != _______\nSET REAR = 0\nELSE\nSET REAR = __________\n[END OF IF]\nStep 3: SET QUEUE[REAR] = _________\nStep 4: EXIT",
         "Step 1: IF (FRONT = 0 and REAR = MAX - 1) OR (FRONT = REAR + 1)\n"
         "Step 2: IF FRONT = -1 and REAR = -1\n"
         "  SET FRONT = REAR = 0\n"
         "  ELSE IF REAR = MAX - 1 and FRONT != 0\n"
         "  SET REAR = 0\n"
         "  ELSE\n"
         "  SET REAR = REAR + 1\n"
         "Step 3: SET QUEUE[REAR] = NUM\n"
         "Step 4: EXIT"),
        ("Fill in the Missing Programming Code for Circular Queue insert():",
         "void insert() {\n"
         "    int num;\n"
         "    printf(\"\\nEnter the number to be inserted in the queue : \");\n"
         "    scanf(\"%d\", &num);\n"
         "    if ((front == 0 && rear == MAX - 1) || (front == rear + 1))\n"
         "        printf(\"\\n OVERFLOW\");\n"
         "    else if (front == -1 && rear == -1) {\n"
         "        front = rear = 0;\n"
         "        queue[rear] = num;\n"
         "    }\n"
         "    else if (rear == MAX - 1 && front != 0) {\n"
         "        rear = 0;\n"
         "        queue[rear] = num;\n"
         "    }\n"
         "    else {\n"
         "        rear = rear + 1;\n"
         "        queue[rear] = num;\n"
         "    }\n"
         "}")
    ]),

    # Session 12 (312)
    "U3S12SLO1": (12, 1, "Circular Queue - Dequeue Operation", [
        ("Algorithm to delete an element from a circular queue\nStep 1: IF FRONT=________\nWrite UNDERFLOW\nGoto Step 4\nStep 2: SET VAL = __________________\nStep 3: IF FRONT = REAR\nSET FRONT = REAR=______\nELSE\nIF FRONT = ______________\nSET FRONT = 0\nELSE\nSET FRONT = __________________\nStep 4: EXIT",
         "Step 1: IF FRONT = -1\n"
         "Step 2: SET VAL = QUEUE[FRONT]\n"
         "Step 3: IF FRONT = REAR\n"
         "  SET FRONT = REAR = -1\n"
         "  ELSE\n"
         "  IF FRONT = MAX - 1\n"
         "    SET FRONT = 0\n"
         "  ELSE\n"
         "    SET FRONT = FRONT + 1\n"
         "Step 4: EXIT"),
        ("Fill in the Missing Programming Code for Circular Queue delete_element():",
         "int delete_element() {\n"
         "    int val;\n"
         "    if (front == -1) {\n"
         "        printf(\"\\n UNDERFLOW\");\n"
         "        return -1;\n"
         "    }\n"
         "    val = queue[front];\n"
         "    if (front == rear)\n"
         "        front = rear = -1;\n"
         "    else {\n"
         "        if (front == MAX - 1)\n"
         "            front = 0;\n"
         "        else\n"
         "            front = front + 1;\n"
         "    }\n"
         "    return val;\n"
         "}")
    ]),

    "U3S12SLO2": (12, 2, "DEQUE (Double-Ended Queue) - Insertion Operation", [
        ("Fill in the Missing Programming Code: Insert at right of Double-Ended Queue",
         "void insert_right() {\n"
         "    int val;\n"
         "    printf(\"\\nEnter the value to be added:\");\n"
         "    scanf(\"%d\", &val);\n"
         "    if ((left == 0 && right == MAX - 1) || (left == right + 1)) {\n"
         "        printf(\"\\n OVERFLOW\");\n"
         "        return;\n"
         "    }\n"
         "    if (left == -1) {\n"
         "        left = 0;\n"
         "        right = 0;\n"
         "    } else {\n"
         "        if (right == MAX - 1)\n"
         "            right = 0;\n"
         "        else\n"
         "            right = right + 1;\n"
         "    }\n"
         "    deque[right] = val;\n"
         "}"),
        ("Fill in the Missing Programming Code: Insert at left of Double-Ended Queue",
         "void insert_left() {\n"
         "    int val;\n"
         "    printf(\"\\nEnter the value to be added:\");\n"
         "    scanf(\"%d\", &val);\n"
         "    if ((left == 0 && right == MAX - 1) || (left == right + 1)) {\n"
         "        printf(\"\\n OVERFLOW\");\n"
         "        return;\n"
         "    }\n"
         "    if (left == -1) {\n"
         "        left = 0;\n"
         "        right = 0;\n"
         "    } else {\n"
         "        if (left == 0)\n"
         "            left = MAX - 1;\n"
         "        else\n"
         "            left = left - 1;\n"
         "    }\n"
         "    deque[left] = val;\n"
         "}")
    ]),

    # Session 13 (313)
    "U3S13SLO1": (13, 1, "DEQUE (Double-Ended Queue) - Deletion Operation", [
        ("Fill in the Missing Programming Code: Delete at left of Double-Ended Queue",
         "void delete_left() {\n"
         "    if (left == -1) {\n"
         "        printf(\"\\n UNDERFLOW\");\n"
         "        return;\n"
         "    }\n"
         "    printf(\"\\nThe deleted element is : %d\", deque[left]);\n"
         "    if (left == right) {\n"
         "        left = -1;\n"
         "        right = -1;\n"
         "    } else {\n"
         "        if (left == MAX - 1)\n"
         "            left = 0;\n"
         "        else\n"
         "            left = left + 1;\n"
         "    }\n"
         "}"),
        ("Fill in the Missing Programming Code: Delete at right of Double-Ended Queue",
         "void delete_right() {\n"
         "    if (left == -1) {\n"
         "        printf(\"\\n UNDERFLOW\");\n"
         "        return;\n"
         "    }\n"
         "    printf(\"\\nThe element deleted is : %d\", deque[right]);\n"
         "    if (left == right) {\n"
         "        left = -1;\n"
         "        right = -1;\n"
         "    } else {\n"
         "        if (right == 0)\n"
         "            right = MAX - 1;\n"
         "        else\n"
         "            right = right - 1;\n"
         "    }\n"
         "}")
    ]),

    "U3S13SLO2": (13, 2, "DEQUE - Advantages, Disadvantages and Applications", [
        ("1. A deque allows ____ and ____ from both ends.", "insertion and deletion"),
        ("2. Deques are more ____ than standard queues for certain applications.", "flexible / versatile"),
        ("3. A deque can function as both a ____ and a ____.", "stack and a queue"),
        ("4. Deques provide efficient ____ complexity for insertion and deletion at both ends.", "O(1) constant time"),
        ("5. Deques are useful in implementing algorithms like ____ sliding window problems.", "maximum / minimum"),
        ("6. Deques require more complex ____ logic compared to simple queues.", "pointer and index manipulation"),
        ("7. Managing both ends in a deque can increase the chance of ____ errors.", "implementation / boundary"),
        ("8. Deques may require more ____ to track front and rear positions.", "variables / memory"),
        ("9. Linked list implementation of deques increases memory usage due to ____.", "double pointers (prev and next)"),
        ("10. Deques are used in ____ scheduling algorithms where elements are added or removed from both ends.", "work-stealing / processor"),
        ("11. In ____ problems, deques help maintain a sliding window of elements.", "sliding window maximum"),
        ("12. Deques can be used to implement both ____ and ____ data structures.", "LIFO (stack) and FIFO (queue)")
    ]),

    # Session 14 (314)
    "U3S14SLO1": (14, 1, "Inserting an Element into the Priority Queue", [
        ("Fill in the Missing Programming Code for Priority Queue insert():",
         "struct node *insert(struct node *start) {\n"
         "    int val, pri;\n"
         "    struct node *ptr, *new_node;\n"
         "    new_node = (struct node *)malloc(sizeof(struct node));\n"
         "    printf(\"\\nEnter the value and its priority : \");\n"
         "    scanf(\"%d %d\", &val, &pri);\n"
         "    new_node->data = val;\n"
         "    new_node->priority = pri;\n"
         "    if (start == NULL || pri < start->priority) {\n"
         "        new_node->next = start;\n"
         "        start = new_node;\n"
         "    } else {\n"
         "        ptr = start;\n"
         "        while (ptr->next != NULL && ptr->next->priority <= pri)\n"
         "            ptr = ptr->next;\n"
         "        new_node->next = ptr->next;\n"
         "        ptr->next = new_node;\n"
         "    }\n"
         "    return start;\n"
         "}")
    ]),

    "U3S14SLO2": (14, 2, "Deleting an Element from the Priority Queue", [
        ("Fill in the Missing Programming Code for Priority Queue delete():",
         "struct node *delete(struct node *start) {\n"
         "    struct node *ptr;\n"
         "    if (start == NULL) {\n"
         "        printf(\"\\n UNDERFLOW\");\n"
         "        return start;\n"
         "    } else {\n"
         "        ptr = start;\n"
         "        printf(\"\\n Deleted item is: %d\", ptr->data);\n"
         "        start = start->next;\n"
         "        free(ptr);\n"
         "    }\n"
         "    return start;\n"
         "}")
    ])
}

def build_docx_files():
    print("=" * 60)
    print(f"Generating All 28 Unit 3 Documents for {STUDENT_NAME} ({REG_NO})")
    print("=" * 60)
    
    for key, (session_num, slo_num, title, qa_pairs) in sorted(SOLUTIONS.items()):
        doc = docx.Document()
        for s in doc.sections:
            s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1.0)
            
        p = doc.add_paragraph(STUDENT_NAME); p.paragraph_format.space_after = Pt(2)
        p = doc.add_paragraph(REG_NO); p.paragraph_format.space_after = Pt(8)
        p = doc.add_paragraph(SUBJECT); p.paragraph_format.space_after = Pt(8)
        p = doc.add_paragraph(f"Unit 3, S{session_num}, SLO{slo_num} - {title}"); p.paragraph_format.space_after = Pt(16)
        
        for q, a in qa_pairs:
            p_q = doc.add_paragraph()
            run_q = p_q.add_run(q)
            run_q.bold = True
            p_q.paragraph_format.space_before = Pt(8)
            p_q.paragraph_format.space_after = Pt(2)
            
            p_a = doc.add_paragraph()
            p_a.add_run("Answer: " + a)
            p_a.paragraph_format.space_after = Pt(8)
            
        filename = f"{key}.docx"
        save_path = DOCX_DIR / filename
        doc.save(str(save_path))
        print(f" [OK] Generated {filename}")

def generate_all_pdfs():
    print("\n--- Batch Generating all 28 PDFs using ReportLab Platypus ---")
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#002060'),
        spaceAfter=10
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        spaceAfter=2
    )
    q_style = ParagraphStyle(
        'DocQ',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.black,
        spaceBefore=6,
        spaceAfter=2
    )
    a_style = ParagraphStyle(
        'DocA',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1a1a1a'),
        leftIndent=12,
        spaceAfter=6
    )

    for key, (session_num, slo_num, title, qa_pairs) in sorted(SOLUTIONS.items()):
        pdf_path = PDF_DIR / f"{key}.pdf"
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        story = []
        story.append(Paragraph(html.escape(STUDENT_NAME), meta_style))
        story.append(Paragraph(html.escape(REG_NO), meta_style))
        story.append(Paragraph(html.escape(SUBJECT), meta_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Unit 3, S{session_num}, SLO{slo_num} - {html.escape(title)}</b>", title_style))
        story.append(Spacer(1, 6))
        
        for q, a in qa_pairs:
            q_formatted = html.escape(q).replace("\n", "<br/>")
            a_formatted = html.escape(a).replace("\n", "<br/>")
            story.append(Paragraph(q_formatted, q_style))
            story.append(Paragraph(f"<b>Answer:</b> {a_formatted}", a_style))
            
        doc.build(story)
        print(f"  [OK] {pdf_path.name} ({pdf_path.stat().st_size} bytes)")

if __name__ == "__main__":
    build_docx_files()
    generate_all_pdfs()
    print("\nAll 28 Unit 3 Documents successfully generated and converted to PDF!")
