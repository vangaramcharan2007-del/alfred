"""
Autonomous Unit 2 Solver & Document Engine for SRM eCurricula (21CSC201J - DSA).
Generates full DOCX worksheets for RAM CHARAN VANGA (RA2511027010164) and converts them to PDF.
Covers all 14 Sessions (201 to 214), SLO 1 and SLO 2 (28 total files).
"""

import os
import sys
from pathlib import Path
import docx
from docx.shared import Pt, Inches, RGBColor

STUDENT_NAME = "RAM CHARAN VANGA"
REG_NO = "RA2511027010164"
SUBJECT = "Sub ject : DSA"

OUT_DIR = Path("outputs/srm_unit2_solved")
DOCX_DIR = OUT_DIR / "docx"
PDF_DIR = OUT_DIR / "pdfs"

DOCX_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

# Complete solutions dictionary for all 28 worksheets
SOLUTIONS = {
    # Session 1 (201)
    "U2S1SLO1": (1, 1, "Fundamentals of Arrays and their Operations", [
        ("1. An array is a collection of elements stored in ____ memory locations.", "contiguous"),
        ("2. The index of the first element in an array is usually ____.", "0 (zero)"),
        ("3. To access the 5th element in an array named arr, we use ____.", "arr[4]"),
        ("4. The operation to add an element at the end of an array (in dynamic arrays) is called ____.", "append / push_back"),
        ("5. The process of finding the position of an element in an array is known as ____.", "searching"),
        ("6. Inserting an element in the middle of an array requires ____ the elements.", "shifting"),
        ("7. Arrays in C are declared using the ____ operator followed by the size in square brackets.", "subscript ([])"),
        ("8. A ____ array has two dimensions and is often used to represent matrices.", "2D (two-dimensional)"),
        ("9. Arrays store elements of the ____ data type.", "same (homogeneous)"),
        ("10. The number of elements an array can hold is known as its ____.", "size / capacity"),
        ("11. Arrays can be ____ or multi-dimensional.", "one-dimensional (single-dimensional)"),
        ("12. The operation to remove an element from a specific position in an array is called ____.", "deletion"),
        ("13. In C, the array index must always be a(n) ____ value.", "integer"),
        ("14. Arrays are ____ in size once declared in static programming languages like C.", "fixed (static)"),
        ("15. A loop commonly used to traverse an array is the ____ loop.", "for loop")
    ]),
    
    "U2S1SLO2": (1, 2, "Inserting an Element into an Array", [
        ("Algorithm to append a new element VAL to an existing array\nStep 1 : Set upper_bound = _________________\nStep 2 : Set A[ __________ ] = _______\nStep 3 : EXIT",
         "Step 1: upper_bound + 1\nStep 2: A[ upper_bound ] = VAL\nStep 3: EXIT"),
        ("Algorithm to insert an element VAL in the middle of an array given a position POS\nStep 1 : [INITIALIZATION] SET I=N\nStep 2 : Repeat Steps 3 and 4 while I >= _______\nStep 3 :  SET A[ _____ ] = A[ __ ]\nStep 4 :  SET I = _______\n[END OF LOOP]\nStep 5 : SET N = _______\nStep 6 : SET A[POS] = ________\nStep 7 : EXIT",
         "Step 2: while I >= POS\nStep 3: SET A[ I + 1 ] = A[ I ]\nStep 4: SET I = I - 1\nStep 5: SET N = N + 1\nStep 6: SET A[POS] = VAL\nStep 7: EXIT")
    ]),

    # Session 2 (202)
    "U2S2SLO1": (2, 1, "Deleting an Element from an Array", [
        ("Algorithm to delete the last element of an array\nStep 1 : SET upper_bound = ____________________\nStep 2 : EXIT",
         "Step 1: SET upper_bound = upper_bound - 1\nStep 2: EXIT"),
        ("Algorithm to delete an element from the middle of an array given position POS\nStep 1 : [INITIALIZATION] SET I = _____\nStep 2 : Repeat Steps 3 and 4 while I <= _______\nStep 3 :  SET A[I] = ________\nStep 4 :  SET I = _______\n[END OF LOOP]\nStep 5 : SET N = ______\nStep 6 : EXIT",
         "Step 1: SET I = POS\nStep 2: Repeat Steps 3 and 4 while I <= N - 1\nStep 3: SET A[I] = A[I + 1]\nStep 4: SET I = I + 1\nStep 5: SET N = N - 1\nStep 6: EXIT")
    ]),

    "U2S2SLO2": (2, 2, "Traversal and Searching in an Array", [
        ("Algorithm for array traversal\nStep 1 : [INITIALIZATION] SET I= ____________\nStep 2 : Repeat Steps 3 to 4 while I <= _____________\nStep 3 :  Apply Process to ____\nStep 4 :  SET I = _________\n[END OF LOOP]\nStep 5 : EXIT",
         "Step 1: SET I = 0 (or lower_bound)\nStep 2: while I <= upper_bound (or N - 1)\nStep 3: Apply Process to A[I]\nStep 4: SET I = I + 1\nStep 5: EXIT"),
        ("1. To access each element of an array, we use a _____.", "loop (or index subscript)"),
        ("2. Array traversal typically starts at index __.", "0"),
        ("3. The last index of an array with n elements is _____.", "n - 1"),
        ("4. While traversing an array, we must ensure the index does not go out of _____.", "bounds (range)"),
        ("5. If we want to traverse an array in reverse, we start from index __.", "n - 1")
    ]),

    # Session 3 (203)
    "U2S3SLO1": (3, 1, "Advantages and Disadvantages of an Array", [
        ("1. Arrays allow __ access to elements using an index.", "random (direct)"),
        ("2. Arrays store elements in __ memory locations.", "contiguous"),
        ("3. Arrays are useful for storing a __ number of similar data types.", "fixed (known)"),
        ("4. The size of an array is __ once declared.", "fixed (static)"),
        ("5. Arrays make it easy to perform __ operations using loops.", "iterative (repetitive)"),
        ("6. Arrays reduce the __ of declaring multiple variables.", "overhead (complexity)"),
        ("7. Memory usage is efficient if the array size is __.", "known in advance"),
        ("8. Arrays provide better performance in terms of __ lookup time.", "O(1) (constant)"),
        ("9. The size of an array must be known at __ time.", "compile"),
        ("10. Arrays have a __ size, which cannot be changed at runtime.", "static (fixed)"),
        ("11. Inserting an element in the middle of an array requires __ other elements.", "shifting"),
        ("12. Deleting an element in an array also involves __ elements.", "shifting"),
        ("13. Wastage of memory can occur if the declared array size is __.", "overestimated (too large)"),
        ("14. Arrays can only store data of the __ type.", "same (homogeneous)"),
        ("15. Searching in an unsorted array takes __ time in the worst case.", "O(n) (linear)")
    ]),

    "U2S3SLO2": (3, 2, "Introduction to Linked Lists", [
        ("1. A linked list, in simple terms, is a __________ of data elements.", "linear collection / sequence"),
        ("2. The data elements in linked lists are called _______.", "nodes"),
        ("3. Linked lists acts as a _________to implement data structures such as stacks, queues, and their variations", "fundamental underlying data structure"),
        ("4. A linked list can be perceived as a _____________ in which each node contains one or more data fields and a pointer to the next node.", "chain of nodes"),
        ("5. In a linked list, every node contains a pointer to another node which is of the same type, it is also called a_______________.", "self-referential structure"),
        ("6. Linked lists contain a pointer variable START that stores the _______________in the list.", "address of the first node (head)"),
        ("7. We can traverse the entire list using ________which contains the address of the first node; the next part of the first node in turn stores the address of its succeeding node", "START (or pointer variable PTR)"),
        ("8. If START = NULL, then the linked _______________________.", "list is empty"),
        ("9. Linked lists provide an efficient way of storing _________ and perform basic operations such as insertion, deletion, and updation of information at the cost of extra space required for storing address of the next node.", "dynamic data"),
        ("10. In C, we can implement a linked list using the following code:\nstruct node\n{\nint ____;\nstruct __________;\n};", "struct node {\n    int data;\n    struct node *next;\n};")
    ]),

    # Session 4 (204)
    "U2S4SLO1": (4, 1, "Array Implementation of Lists - Programming Practice 1", [
        ("1. Find the max and min elements in an array.",
         "#include <stdio.h>\nint main() {\n    int a[] = {25, 11, 7, 75, 56}, n = 5;\n    int max = a[0], min = a[0];\n    for(int i = 1; i < n; i++) {\n        if(a[i] > max) max = a[i];\n        if(a[i] < min) min = a[i];\n    }\n    printf(\"Max: %d, Min: %d\\n\", max, min);\n    return 0;\n}\nOutput: Max: 75, Min: 7"),
        ("2. Count frequency of each element in an array.",
         "#include <stdio.h>\nint main() {\n    int a[] = {1, 2, 8, 3, 2, 2, 8, 5}, n = 8, visited = -1;\n    int fr[8];\n    for(int i = 0; i < n; i++) {\n        int count = 1;\n        for(int j = i + 1; j < n; j++) {\n            if(a[i] == a[j]) { count++; fr[j] = visited; }\n        }\n        if(fr[i] != visited) fr[i] = count;\n    }\n    for(int i = 0; i < n; i++) if(fr[i] != visited) printf(\"%d: %d times\\n\", a[i], fr[i]);\n    return 0;\n}"),
        ("3. Separate out the negatives, positives and zeroes.",
         "#include <stdio.h>\nint main() {\n    int a[] = {-4, 3, 0, -2, 5, 0, 7}, n = 7;\n    printf(\"Positives: \"); for(int i=0;i<n;i++) if(a[i]>0) printf(\"%d \", a[i]);\n    printf(\"\\nNegatives: \"); for(int i=0;i<n;i++) if(a[i]<0) printf(\"%d \", a[i]);\n    printf(\"\\nZeroes: \"); for(int i=0;i<n;i++) if(a[i]==0) printf(\"%d \", a[i]);\n    return 0;\n}"),
        ("4. Reverse the array elements.",
         "#include <stdio.h>\nint main() {\n    int a[] = {10, 20, 30, 40, 50}, n = 5;\n    for(int i = 0; i < n / 2; i++) {\n        int temp = a[i]; a[i] = a[n - 1 - i]; a[n - 1 - i] = temp;\n    }\n    printf(\"Reversed: \"); for(int i=0;i<n;i++) printf(\"%d \", a[i]);\n    return 0;\n}\nOutput: Reversed: 50 40 30 20 10"),
        ("5. Print odd numbers in an array.",
         "#include <stdio.h>\nint main() {\n    int a[] = {12, 17, 19, 24, 33, 40}, n = 6;\n    printf(\"Odd numbers: \");\n    for(int i = 0; i < n; i++) if(a[i] % 2 != 0) printf(\"%d \", a[i]);\n    return 0;\n}\nOutput: Odd numbers: 17 19 33")
    ]),

    "U2S4SLO2": (4, 2, "Array Implementation of Lists - Programming Practice 2", [
        ("1. Find the sum and average of the elements in an array.",
         "#include <stdio.h>\nint main() {\n    int a[] = {10, 20, 30, 40, 50}, n = 5, sum = 0;\n    for(int i = 0; i < n; i++) sum += a[i];\n    printf(\"Sum = %d, Average = %.2f\\n\", sum, (float)sum / n);\n    return 0;\n}\nOutput: Sum = 150, Average = 30.00"),
        ("2. Given a set of elements find the Armstrong numbers.",
         "#include <stdio.h>\n#include <math.h>\nint isArmstrong(int num) {\n    int temp = num, sum = 0, digits = 0;\n    while(temp) { digits++; temp /= 10; }\n    temp = num;\n    while(temp) { sum += pow(temp % 10, digits); temp /= 10; }\n    return sum == num;\n}\nint main() {\n    int a[] = {153, 120, 370, 371, 407, 500}, n = 6;\n    for(int i=0; i<n; i++) if(isArmstrong(a[i])) printf(\"%d is Armstrong\\n\", a[i]);\n    return 0;\n}"),
        ("3. Decimal to octal conversion.",
         "#include <stdio.h>\nvoid decToOctal(int n) {\n    int octal[32], i = 0;\n    while(n != 0) { octal[i++] = n % 8; n /= 8; }\n    printf(\"Octal: \"); for(int j = i - 1; j >= 0; j--) printf(\"%d\", octal[j]); printf(\"\\n\");\n}\nint main() { decToOctal(100); return 0; }\nOutput: Octal: 144"),
        ("4. Sum of even numbers in an array.",
         "#include <stdio.h>\nint main() {\n    int a[] = {1, 2, 3, 4, 5, 6, 7, 8}, n = 8, sum = 0;\n    for(int i = 0; i < n; i++) if(a[i] % 2 == 0) sum += a[i];\n    printf(\"Sum of even numbers = %d\\n\", sum);\n    return 0;\n}\nOutput: Sum of even numbers = 20"),
        ("5. Search an element in an array.",
         "#include <stdio.h>\nint main() {\n    int a[] = {15, 32, 47, 58, 64}, n = 5, key = 47, found = -1;\n    for(int i = 0; i < n; i++) if(a[i] == key) { found = i; break; }\n    if(found != -1) printf(\"Element %d found at index %d\\n\", key, found);\n    else printf(\"Not found\\n\");\n    return 0;\n}\nOutput: Element 47 found at index 2")
    ]),

    # Session 5 (205)
    "U2S5SLO1": (5, 1, "Singly Linked List – Traversal and Searching", [
        ("Algorithm for traversing a linked list\nStep 1: [INITIALIZE] SET PTR = _________\nStep 2: Repeat Steps 3 and 4 while ____________\nStep 3:  Apply Process to __________\nStep 4:  SET PTR = ____________\n[END OF LOOP]\nStep 5: EXIT",
         "Step 1: SET PTR = START\nStep 2: Repeat Steps 3 and 4 while PTR != NULL\nStep 3: Apply Process to PTR -> DATA\nStep 4: SET PTR = PTR -> NEXT\nStep 5: EXIT"),
        ("Algorithm to print the number of nodes in a linked list\nStep 1: [INITIALIZE] SET COUNT = 0\nStep 2: [INITIALIZE] SET ___________\nStep 3: Repeat Steps 4 and 5 while ___________\nStep 4:  SET COUNT = ____________\nStep 5:  SET PTR = ___________\n[END OF LOOP]\nStep 6: Write _________\nStep 7: EXIT",
         "Step 2: SET PTR = START\nStep 3: Repeat Steps 4 and 5 while PTR != NULL\nStep 4: SET COUNT = COUNT + 1\nStep 5: SET PTR = PTR -> NEXT\nStep 6: Write COUNT\nStep 7: EXIT"),
        ("Algorithm to search a linked list\nStep 1: [INITIALIZE] SET PTR = ______\nStep 2: Repeat Step 3 while PTR != _______\nStep 3:  IF VAL = ____________\nSET POS = ________\nGo To Step 5\nELSE\nSET PTR = _________\n[END OF IF]\n[END OF LOOP]\nStep 4: SET POS = _______\nStep 5: EXIT",
         "Step 1: SET PTR = START\nStep 2: Repeat Step 3 while PTR != NULL\nStep 3: IF VAL = PTR -> DATA\nSET POS = PTR\nGo To Step 5\nELSE\nSET PTR = PTR -> NEXT\nStep 4: SET POS = NULL (or -1)\nStep 5: EXIT")
    ]),

    "U2S5SLO2": (5, 2, "Singly Linked List – Insertion at Beginning and End", [
        ("Algorithm to insert a new node VAL at the beginning\nStep 1: IF AVAIL = NULL\nWrite _____________\nGo to Step 7\n[END OF IF]\nStep 2: SET NEW_NODE = __________\nStep 3: SET AVAIL = ________________\nStep 4: SET ____________________ = VAL\nStep 5: SET ____________________ = START\nStep 6: SET START = ___________\nStep 7: EXIT",
         "Step 1: Write OVERFLOW\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET NEW_NODE -> DATA = VAL\nStep 5: SET NEW_NODE -> NEXT = START\nStep 6: SET START = NEW_NODE\nStep 7: EXIT"),
        ("Algorithm to insert a new node at the end\nStep 1: IF AVAIL = ________\nWrite OVERFLOW\nGo to Step 10\n[END OF IF]\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET NEW_NODE -> DATA = _______\nStep 5: SET NEW_NODE -> NEXT = _______\nStep 6: SET PTR = ________\nStep 7: Repeat Step 8 while PTR -> _______ != NULL\nStep 8:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 9: SET PTR -> NEXT = ____________\nStep 10: EXIT",
         "Step 1: IF AVAIL = NULL\nStep 4: SET NEW_NODE -> DATA = VAL\nStep 5: SET NEW_NODE -> NEXT = NULL\nStep 6: SET PTR = START\nStep 7: while PTR -> NEXT != NULL\nStep 8: SET PTR = PTR -> NEXT\nStep 9: SET PTR -> NEXT = NEW_NODE\nStep 10: EXIT")
    ]),

    # Session 6 (206)
    "U2S6SLO1": (6, 1, "Singly Linked List – Insertion at the Middle", [
        ("Algorithm to insert a new node VAL after a node that has value NUM\nStep 1: IF AVAIL = NULL\nWrite OVERFLOW\nGo to Step 12\n[END OF IF]\nStep 2: SET NEW_NODE = ________\nStep 3: SET AVAIL = ______________\nStep 4: SET NEW_NODE -> DATA = _______\nStep 5: SET PTR = ________\nStep 6: SET PREPTR = ______\nStep 7: Repeat Steps 8 and 9 while _____________ != NUM\nStep 8:  SET PREPTR = _____\nStep 9:  SET PTR = ______________\n[END OF LOOP]\nStep 10: _____________ = NEW_NODE\nStep 11: SET NEW_NODE -> NEXT = ______\nStep 12: EXIT",
         "Step 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET NEW_NODE -> DATA = VAL\nStep 5: SET PTR = START\nStep 6: SET PREPTR = PTR\nStep 7: while PREPTR -> DATA != NUM\nStep 8: SET PREPTR = PTR\nStep 9: SET PTR = PTR -> NEXT\nStep 10: PREPTR -> NEXT = NEW_NODE\nStep 11: SET NEW_NODE -> NEXT = PTR\nStep 12: EXIT"),
        ("Algorithm to insert a new node VAL before a node that has value NUM\nStep 1: IF AVAIL = NULL\nWrite OVERFLOW\nGo to Step 12\n[END OF IF]\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET ___________ = VAL\nStep 5: SET ______ = START\nStep 6: SET _________ = PTR\nStep 7: Repeat Steps 8 and 9 while __________ != NUM\nStep 8:  SET _________ = PTR\nStep 9:  SET PTR = ______________\n[END OF LOOP]\nStep 10: SET ______________ = NEW_NODE\nStep 11: SET NEW_NODE -> NEXT = ______\nStep 12: EXIT",
         "Step 4: SET NEW_NODE -> DATA = VAL\nStep 5: SET PTR = START\nStep 6: SET PREPTR = PTR\nStep 7: while PTR -> DATA != NUM\nStep 8: SET PREPTR = PTR\nStep 9: SET PTR = PTR -> NEXT\nStep 10: SET PREPTR -> NEXT = NEW_NODE\nStep 11: SET NEW_NODE -> NEXT = PTR\nStep 12: EXIT")
    ]),

    "U2S6SLO2": (6, 2, "Singly Linked List – Deletion at Beginning and End", [
        ("Algorithm to delete the first node\nStep 1: IF START = NULL\nWrite ___________\nGo to Step 5\n[END OF IF]\nStep 2: SET PTR = ________\nStep 3: SET START = _____________\nStep 4: FREE _____\nStep 5: EXIT",
         "Step 1: Write UNDERFLOW\nStep 2: SET PTR = START\nStep 3: SET START = START -> NEXT\nStep 4: FREE PTR\nStep 5: EXIT"),
        ("Algorithm to delete the last node\nStep 1: IF ______________\nWrite UNDERFLOW\nGo to Step 8\n[END OF IF]\nStep 2: SET PTR = ________\nStep 3: Repeat Steps 4 and 5 while PTR -> NEXT != _______\nStep 4:  SET ________ = PTR\nStep 5:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 6: SET _____________ = NULL\nStep 7: FREE _______\nStep 8: EXIT",
         "Step 1: IF START = NULL\nStep 2: SET PTR = START\nStep 3: while PTR -> NEXT != NULL\nStep 4: SET PREPTR = PTR\nStep 5: SET PTR = PTR -> NEXT\nStep 6: SET PREPTR -> NEXT = NULL\nStep 7: FREE PTR\nStep 8: EXIT")
    ]),

    # Session 7 (207)
    "U2S7SLO1": (7, 1, "Singly Linked List – Deletion at the Middle", [
        ("Algorithm to delete the node after a given node NUM\nStep 1: IF START = NULL\nWrite UNDERFLOW\nGo to Step 10\n[END OF IF]\nStep 2: SET ______ = START\nStep 3: SET _______ = PTR\nStep 4: Repeat Steps 5 and 6 while ______________ != NUM\nStep 5:  SET PREPTR = ________\nStep 6:  SET PTR = _______________\n[END OF LOOP]\nStep 7: SET TEMP = _________\nStep 8: SET PREPTR -> NEXT = ______________\nStep 9: FREE ___________\nStep 10 : EXIT",
         "Step 2: SET PTR = START\nStep 3: SET PREPTR = PTR\nStep 4: while PREPTR -> DATA != NUM\nStep 5: SET PREPTR = PTR\nStep 6: SET PTR = PTR -> NEXT\nStep 7: SET TEMP = PTR\nStep 8: SET PREPTR -> NEXT = PTR -> NEXT\nStep 9: FREE TEMP\nStep 10: EXIT")
    ]),

    "U2S7SLO2": (7, 2, "Singly Linked List – Implementation of Linked Lists", [
        ("1. A linked list is a collection of ___, where each node contains data and a pointer to the _____.", "nodes, next node"),
        ("2. In C, the keyword ____ is used to define a node in a linked list.", "struct"),
        ("3. The pointer used to point to the first node of the linked list is called the ____.", "head / START"),
        ("4. The pointer in the last node of a singly linked list points to ____.", "NULL"),
        ("5. A node in a linked list typically contains two fields: ____ and ____.", "data, next (pointer)"),
        ("6. Dynamic memory allocation for a new node is done using the ____ function.", "malloc()")
    ]),

    # Session 8 (208)
    "U2S8SLO1": (8, 1, "Singly Linked List – Implementation of Linked Lists", [
        ("1. To traverse a linked list, a ____ pointer is used to iterate through each node.", "temporary (PTR)"),
        ("2. To insert a node at the beginning of the linked list, update the new node’s link to point to the ____.", "current head (START)"),
        ("3. After inserting a node at the beginning, the ____ must be updated to point to the new node.", "head (START) pointer"),
        ("4. To delete a node, it’s important to ____ the memory after unlinking the node.", "free"),
        ("5. A ____ check should always be done before accessing a node’s data through a pointer.", "NULL pointer"),
        ("6. Inserting a node at the end requires traversal until the node’s ____ pointer is NULL.", "next")
    ]),

    "U2S8SLO2": (8, 2, "Circular Singly Linked List - Insertion", [
        ("Algorithm to insert a new node VAL at the beginning\nStep 1: IF AVAIL = NULL\nWrite OVERFLOW\nGo to Step 11\n[END OF IF]\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = _________________\nStep 4: SET _______________ = VAL\nStep 5: SET PTR = ___________\nStep 6: Repeat Step 7 while ________________ != START\nStep 7:  PTR = _____________\n[END OF LOOP]\nStep 8: SET ______________ = START\nStep 9: SET _______________ = NEW_NODE\nStep 10: SET START = ___________\nStep 11: EXIT",
         "Step 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET NEW_NODE -> DATA = VAL\nStep 5: SET PTR = START\nStep 6: while PTR -> NEXT != START\nStep 7: PTR = PTR -> NEXT\nStep 8: SET NEW_NODE -> NEXT = START\nStep 9: SET PTR -> NEXT = NEW_NODE\nStep 10: SET START = NEW_NODE\nStep 11: EXIT"),
        ("Algorithm to insert a new node at the end\nStep 1: IF AVAIL = NULL\nWrite OVERFLOW\nGo to Step 10\n[END OF IF]\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET _____________________ = VAL\nStep 5: SET _____________________ = START\nStep 6: SET PTR = START\nStep 7: Repeat Step 8 while ___________ != START\nStep 8:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 9: SET ______________ = NEW_NODE\nStep 10: EXIT",
         "Step 4: SET NEW_NODE -> DATA = VAL\nStep 5: SET NEW_NODE -> NEXT = START\nStep 6: SET PTR = START\nStep 7: while PTR -> NEXT != START\nStep 8: SET PTR = PTR -> NEXT\nStep 9: SET PTR -> NEXT = NEW_NODE\nStep 10: EXIT")
    ]),

    # Session 9 (209)
    "U2S9SLO1": (9, 1, "Circular Singly Linked List - Deletion", [
        ("Algorithm to delete the first node\nStep 1: IF START = NULL\nWrite UNDERFLOW\nGo to Step 8\n[END OF IF]\nStep 2: SET PTR = ___________\nStep 3: Repeat Step 4 while PTR -> NEXT != __________\nStep 4:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 5: SET ____________ = START -> NEXT\nStep 6: FREE _________\nStep 7: SET START = _____________\nStep 8: EXIT",
         "Step 2: SET PTR = START\nStep 3: while PTR -> NEXT != START\nStep 4: SET PTR = PTR -> NEXT\nStep 5: SET PTR -> NEXT = START -> NEXT\nStep 6: FREE START\nStep 7: SET START = PTR -> NEXT\nStep 8: EXIT"),
        ("Algorithm to delete the last node\nStep 1: IF START = NULL\nWrite UNDERFLOW\nGo to Step 8\n[END OF IF]\nStep 2: SET PTR = START\nStep 3: Repeat Steps 4 and 5 while _______________ != START\nStep 4:  SET ___________ = PTR\nStep 5:  SET PTR = ________________\n[END OF LOOP]\nStep 6: SET ______________ = START\nStep 7: FREE _______\nStep 8: EXIT",
         "Step 3: while PTR -> NEXT != START\nStep 4: SET PREPTR = PTR\nStep 5: SET PTR = PTR -> NEXT\nStep 6: SET PREPTR -> NEXT = START\nStep 7: FREE PTR\nStep 8: EXIT")
    ]),

    "U2S9SLO2": (9, 2, "Doubly Linked List - Introduction", [
        ("1. In a doubly linked list, each node contains __ pointers.", "two (2)"),
        ("2. The two pointers in a doubly linked list point to the __ and the __ nodes.", "previous, next"),
        ("3. The pointer to the next node in a doubly linked list is commonly called __.", "next"),
        ("4. The pointer to the previous node in a doubly linked list is commonly called __.", "prev"),
        ("5. In a doubly linked list, the previous pointer of the head node is always set to __.", "NULL"),
        ("6. In a doubly linked list, the next pointer of the tail node is always set to __.", "NULL"),
        ("7. Insertion at the beginning of a doubly linked list requires updating the __ pointer of the old head node.", "prev"),
        ("8. Deletion of a node in a doubly linked list requires adjusting the pointers of its __ and __ nodes.", "previous, next"),
        ("9. Traversing a doubly linked list can be done in both __ and __ directions.", "forward, backward"),
        ("10. A doubly linked list allows for more efficient deletion operations compared to a __ linked list.", "singly")
    ]),

    # Session 10 (210)
    "U2S10SLO1": (10, 1, "Doubly Linked List – Insertion at Beginning and End", [
        ("Algorithm to insert a new node VAL at the beginning\nStep 1: IF AVAIL = NULL\nWrite OVERFLOW\nGo to Step 9\n[END OF IF]\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET NEW_NODE -> DATA = __________\nStep 5: SET NEW_NODE -> PREV = _________\nStep 6: SET NEW_NODE -> NEXT = _________\nStep 7: SET ______________ = NEW_NODE\nStep 8: SET START = ________________\nStep 9: EXIT",
         "Step 4: SET NEW_NODE -> DATA = VAL\nStep 5: SET NEW_NODE -> PREV = NULL\nStep 6: SET NEW_NODE -> NEXT = START\nStep 7: SET START -> PREV = NEW_NODE\nStep 8: SET START = NEW_NODE\nStep 9: EXIT"),
        ("Algorithm to insert a new node VAL at the end\nStep 1: IF AVAIL = NULL\nWrite OVERFLOW\nGo to Step 11\n[END OF IF]\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET _________________ = VAL\nStep 5: SET __________________ = NULL\nStep 6: SET PTR = START\nStep 7: Repeat Step 8 while _____________ != NULL\nStep 8:   SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 9: SET __________ = NEW_NODE\nStep 10: SET _______________ = PTR\nStep 11: EXIT",
         "Step 4: SET NEW_NODE -> DATA = VAL\nStep 5: SET NEW_NODE -> NEXT = NULL\nStep 6: SET PTR = START\nStep 7: while PTR -> NEXT != NULL\nStep 8: SET PTR = PTR -> NEXT\nStep 9: SET PTR -> NEXT = NEW_NODE\nStep 10: SET NEW_NODE -> PREV = PTR\nStep 11: EXIT")
    ]),

    "U2S10SLO2": (10, 2, "Doubly Linked List – Insertion at Middle", [
        ("Algorithm to insert a new node VAL after a given node NUM\nStep 1: IF AVAIL = NULL\nWrite OVERFLOW\nGo to Step 12\n[END OF IF]\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET ___________________ = VAL\nStep 5: SET PTR = START\nStep 6: Repeat Step 7 while PTR -> DATA != ________\nStep 7:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 8: SET NEW_NODE  -> NEXT = _______________\nStep 9: SET __________________ = PTR\nStep 10: SET _____________ = NEW_NODE\nStep 11: SET ______________________ = NEW_NODE\nStep 12: EXIT",
         "Step 4: SET NEW_NODE -> DATA = VAL\nStep 6: while PTR -> DATA != NUM\nStep 7: SET PTR = PTR -> NEXT\nStep 8: SET NEW_NODE -> NEXT = PTR -> NEXT\nStep 9: SET NEW_NODE -> PREV = PTR\nStep 10: SET PTR -> NEXT -> PREV = NEW_NODE\nStep 11: SET PTR -> NEXT = NEW_NODE\nStep 12: EXIT"),
        ("Algorithm to insert a new node VAL before a given node NUM\nStep 1: IF AVAIL = NULL\nWrite OVERFLOW\nGo to Step 12\n[END OF IF]\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET _________________ = VAL\nStep 5: SET PTR = START\nStep 6: Repeat Step 7 while ________________ != NUM\nStep 7:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 8: SET NEW_NODE  -> NEXT = _______\nStep 9: SET NEW_NODE -> PREV = ________________\nStep 10: SET ______________ = NEW_NODE\nStep 11: SET _____________________ = NEW_NODE\nStep 12: EXIT",
         "Step 4: SET NEW_NODE -> DATA = VAL\nStep 6: while PTR -> DATA != NUM\nStep 7: SET PTR = PTR -> NEXT\nStep 8: SET NEW_NODE -> NEXT = PTR\nStep 9: SET NEW_NODE -> PREV = PTR -> PREV\nStep 10: SET PTR -> PREV -> NEXT = NEW_NODE\nStep 11: SET PTR -> PREV = NEW_NODE\nStep 12: EXIT")
    ]),

    # Session 11 (211)
    "U2S11SLO1": (11, 1, "Doubly Linked List – Deletion at Beginning and End", [
        ("Algorithm to delete the first node\nStep 1: IF START = NULL\nWrite UNDERFLOW\nGo to Step 6\n[END OF IF]\nStep 2: SET PTR = ____________\nStep 3: SET START = ___________________\nStep 4: SET ______________ = NULL\nStep 5: FREE _______\nStep 6: EXIT",
         "Step 2: SET PTR = START\nStep 3: SET START = START -> NEXT\nStep 4: SET START -> PREV = NULL\nStep 5: FREE PTR\nStep 6: EXIT"),
        ("Algorithm to delete the last node\nStep 1: IF START = NULL\nWrite UNDERFLOW\nGo to Step 7\n[END OF IF]\nStep 2: SET PTR = ____________\nStep 3: Repeat Step 4 while ____________ != NULL\nStep 4:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 5: SET _____________________ = NULL\nStep 6: FREE ___________\nStep 7: EXIT",
         "Step 2: SET PTR = START\nStep 3: while PTR -> NEXT != NULL\nStep 4: SET PTR = PTR -> NEXT\nStep 5: SET PTR -> PREV -> NEXT = NULL\nStep 6: FREE PTR\nStep 7: EXIT")
    ]),

    "U2S11SLO2": (11, 2, "Doubly Linked List – Deletion at Middle", [
        ("Algorithm to delete a node after a given node NUM\nStep 1: IF START = NULL\nWrite UNDERFLOW\nGo to Step 9\n[END OF IF]\nStep 2: SET PTR = __________\nStep 3: Repeat Step 4 while PTR -> DATA != _________\nStep 4:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 5: SET TEMP = _____________\nStep 6: SET PTR -> NEXT = ______________\nStep 7: SET _______________________ = PTR\nStep 8: FREE _________\nStep 9: EXIT",
         "Step 2: SET PTR = START\nStep 3: while PTR -> DATA != NUM\nStep 4: SET PTR = PTR -> NEXT\nStep 5: SET TEMP = PTR -> NEXT\nStep 6: SET PTR -> NEXT = TEMP -> NEXT\nStep 7: SET TEMP -> NEXT -> PREV = PTR\nStep 8: FREE TEMP\nStep 9: EXIT"),
        ("Algorithm to delete a node before a given node NUM\nStep 1: IF START = NULL\nWrite UNDERFLOW\nGo to Step 9\n[END OF IF]\nStep 2: SET PTR = _________\nStep 3: Repeat Step 4 while ________________ != NUM\nStep 4:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 5: SET TEMP = ______________\nStep 6: SET __________________________ = PTR\nStep 7: SET ________________ = TEMP -> PREV\nStep 8: FREE __________\nStep 9: EXIT",
         "Step 2: SET PTR = START\nStep 3: while PTR -> DATA != NUM\nStep 4: SET PTR = PTR -> NEXT\nStep 5: SET TEMP = PTR -> PREV\nStep 6: SET TEMP -> PREV -> NEXT = PTR\nStep 7: SET PTR -> PREV = TEMP -> PREV\nStep 8: FREE TEMP\nStep 9: EXIT")
    ]),

    # Session 12 (212)
    "U2S12SLO1": (12, 1, "Implementation of Doubly Linked Lists", [
        ("1. A doubly linked list node typically contains data, a pointer to the next node, and a pointer to the __ node.", "previous"),
        ("2. The structure of a doubly linked list node in C often uses the keyword __.", "struct"),
        ("3. In C, to create a node dynamically, we use the function __.", "malloc()"),
        ("4. The first node of a doubly linked list is called the __.", "head / START"),
        ("5. To insert a node at the beginning, the new node’s next pointer should point to the __ node.", "head (current first)"),
        ("6. When inserting at the beginning, the previous pointer of the old head should point to the __ node.", "new"),
        ("7. To insert a node at the end, we must traverse the list until we find the node whose next is __.", "NULL"),
        ("8. While inserting at the end, the new node’s previous pointer should point to the __ node.", "last (tail / PTR)"),
        ("9. To delete the first node, we move the head pointer to the __ node.", "next (second)"),
        ("10. When deleting the first node, the new head’s previous pointer must be set to __.", "NULL")
    ]),

    "U2S12SLO2": (12, 2, "Implementation of Doubly Linked Lists", [
        ("1. To delete the last node, set the next pointer of the previous node to __.", "NULL"),
        ("2. To delete a specific node, update the previous node’s next pointer and the next node’s __ pointer.", "previous"),
        ("3. A doubly linked list can be traversed in both forward and __ directions.", "backward"),
        ("4. In C, the last node is identified when its next pointer is equal to __.", "NULL"),
        ("5. In a doubly linked list, the head pointer points to the __ node.", "first"),
        ("6. The previous pointer of the head node and the next pointer of the tail node should both be set to __.", "NULL"),
        ("7. When freeing a node in C, we use the function __.", "free()"),
        ("8. A doubly linked list avoids the need for a temporary pointer for backward traversal because of the __ pointer.", "prev"),
        ("9. While inserting after a given node, the new node’s next pointer should point to the given node’s __.", "next node"),
        ("10. In a doubly linked list, each node is connected in __ directions.", "two (both)")
    ]),

    # Session 13 (213)
    "U2S13SLO1": (13, 1, "Circular Doubly Linked Lists - Introduction", [
        ("1. In a circular doubly linked list, the last node’s next pointer points to the ____.", "first node (head / START)"),
        ("2. A circular doubly linked list contains two pointers in each node, typically named ____ and ____.", "next, prev"),
        ("3. In a circular doubly linked list, the first node’s prev pointer points to the ____.", "last node (tail)"),
        ("4. The time complexity to traverse a circular doubly linked list of n nodes is ____.", "O(n)"),
        ("5. Insertion at the beginning of a circular doubly linked list requires updating ____ nodes.", "two (head and tail) / 4 pointers"),
        ("6. The circular nature of the list ensures that no node has a ____ next or previous pointer.", "NULL"),
        ("7. To delete a node from the end of a circular doubly linked list, we must update the prev pointer of the ____ and the next pointer of the ____.", "head (first node), second last node"),
        ("8. The traversal of a circular doubly linked list can start at ____ and loop until we reach it again.", "any node (head)"),
        ("9. In a circular doubly linked list, each node has exactly ____ neighbours.", "two (2)"),
        ("10. Compared to a singly linked list, circular doubly linked lists allow traversal in both ____.", "forward and backward directions")
    ]),

    "U2S13SLO2": (13, 2, "Circular Doubly Linked Lists - Insertion", [
        ("Algorithm to insert a new node VAL at the beginning\nStep 1: IF AVAIL = NULL\nWrite OVERFLOW\nGo to Step 13\n[END OF IF]\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET _____________________ = VAL\nStep 5: SET PTR = _____________\nStep 6: Repeat Step 7 while PTR -> NEXT != __________\nStep 7:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 8: SET ________________ = NEW_NODE\nStep 9: SET ___________________ = PTR\nStep 10: SET _____________________ = START\nStep 11: SET _________________ = NEW_NODE\nStep 12: SET START = _____________\nStep 13: EXIT",
         "Step 4: SET NEW_NODE -> DATA = VAL\nStep 5: SET PTR = START\nStep 6: while PTR -> NEXT != START\nStep 7: SET PTR = PTR -> NEXT\nStep 8: SET PTR -> NEXT = NEW_NODE\nStep 9: SET NEW_NODE -> PREV = PTR\nStep 10: SET NEW_NODE -> NEXT = START\nStep 11: SET START -> PREV = NEW_NODE\nStep 12: SET START = NEW_NODE\nStep 13: EXIT"),
        ("Algorithm to insert a new node VAL at the end\nStep 1: IF AVAIL = NULL\nWrite OVERFLOW\nGo to Step 12\n[END OF IF]\nStep 2: SET NEW_NODE = AVAIL\nStep 3: SET AVAIL = AVAIL -> NEXT\nStep 4: SET NEW_NODE -> DATA = _________\nStep 5: SET NEW_NODE -> NEXT = __________\nStep 6: SET PTR = START\nStep 7: Repeat Step 8 while _____________ != START\nStep 8:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 9: SET PTR -> NEXT = ____________\nStep 10: SET NEW_NODE -> PREV = ________\nStep 11: SET START -> PREV = ________________\nStep 12: EXIT",
         "Step 4: SET NEW_NODE -> DATA = VAL\nStep 5: SET NEW_NODE -> NEXT = START\nStep 6: SET PTR = START\nStep 7: while PTR -> NEXT != START\nStep 8: SET PTR = PTR -> NEXT\nStep 9: SET PTR -> NEXT = NEW_NODE\nStep 10: SET NEW_NODE -> PREV = PTR\nStep 11: SET START -> PREV = NEW_NODE\nStep 12: EXIT")
    ]),

    # Session 14 (214)
    "U2S14SLO1": (14, 1, "Circular Doubly Linked Lists – Deletion", [
        ("Algorithm to delete the first node\nStep 1: IF START = NULL\nWrite UNDERFLOW\nGo to Step 8\n[END OF IF]\nStep 2: SET PTR = START\nStep 3: Repeat Step 4 while ________________ != START\nStep 4:  SET PTR = PTR -> NEXT\n [END OF LOOP]\nStep 5: SET PTR -> NEXT = ______________\nStep 6: SET ___________________________ = PTR\nStep 7: FREE ___________\nStep 8: SET START = _________________",
         "Step 3: while PTR -> NEXT != START\nStep 4: SET PTR = PTR -> NEXT\nStep 5: SET PTR -> NEXT = START -> NEXT\nStep 6: SET START -> NEXT -> PREV = PTR\nStep 7: FREE START\nStep 8: SET START = PTR -> NEXT"),
        ("Algorithm to delete the last node\nStep 1: IF START = NULL\nWrite UNDERFLOW\nGo to Step 8\n[END OF IF]\nStep 2: SET PTR = START\nStep 3: Repeat Step 4 while PTR -> NEXT != ____________\nStep 4:  SET PTR = PTR -> NEXT\n[END OF LOOP]\nStep 5: SET _______________________ = START\nStep 6: SET ___________________ = PTR -> PREV\nStep 7: FREE ________\nStep 8: EXIT",
         "Step 3: while PTR -> NEXT != START\nStep 4: SET PTR = PTR -> NEXT\nStep 5: SET PTR -> PREV -> NEXT = START\nStep 6: SET START -> PREV = PTR -> PREV\nStep 7: FREE PTR\nStep 8: EXIT")
    ]),

    "U2S14SLO2": (14, 2, "Applications - Sparse Matrix, Polynomial Arithmetic, Josephus Problem", [
        ("1. In a sparse matrix, most of the elements are __.", "zero (0)"),
        ("2. A linked list is preferred for representing sparse matrices to save __.", "memory (space)"),
        ("3. Each node in the linked list representation of a sparse matrix typically stores row index, column index, and the __.", "value (non-zero element)"),
        ("4. Using linked lists for sparse matrices allows efficient __ of non-zero elements.", "storage and manipulation"),
        ("5. Compared to a 2D array, a linked list avoids storing multiple __ elements in a sparse matrix.", "zero"),
        ("6. In the linked‐list representation of a polynomial, each node typically contains a coefficient and an __.", "exponent (power)"),
        ("7. To add two polynomials represented as linked lists, you traverse both lists simultaneously and merge nodes with the same __.", "exponent (power)"),
        ("8. In polynomial multiplication using linked lists, for each term in the first list, you multiply it by every term in the second list and insert the result into a __ linked list.", "result (new)"),
        ("9. When inserting a new term into the result list during multiplication, if a node with the same exponent already exists, you simply add to its __.", "coefficient"),
        ("10. Keeping the linked list of polynomial terms in descending order of exponents simplifies operations like addition, subtraction, and __.", "multiplication / evaluation"),
        ("11. The Josephus problem is a theoretical problem related to a certain elimination game in a __.", "circle"),
        ("12. A __ linked list is often used to simulate the Josephus problem efficiently.", "circular"),
        ("13. In the Josephus problem, counting proceeds around the circle and every __ person is eliminated.", "k-th (m-th)"),
        ("14. Using a circular linked list, we can efficiently move from one node to the __ during elimination.", "next"),
        ("15. The last remaining person in the Josephus problem is called the __.", "survivor / leader")
    ])
}


def build_docx_files():
    print("=" * 60)
    print(f"Generating All 28 Unit 2 Documents for {STUDENT_NAME} ({REG_NO})")
    print("=" * 60)
    
    for key, (session_num, slo_num, title, qa_pairs) in sorted(SOLUTIONS.items()):
        doc = docx.Document()
        for s in doc.sections:
            s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1.0)
            
        p = doc.add_paragraph(STUDENT_NAME); p.paragraph_format.space_after = Pt(2)
        p = doc.add_paragraph(REG_NO); p.paragraph_format.space_after = Pt(8)
        p = doc.add_paragraph(SUBJECT); p.paragraph_format.space_after = Pt(8)
        p = doc.add_paragraph(f"Unit 2, S{session_num}, SLO{slo_num} - {title}"); p.paragraph_format.space_after = Pt(16)
        
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
    import html
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib import colors

    styles = getSampleStyleSheet()
    
    # Custom styles
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
        # Header / Student Info
        story.append(Paragraph(html.escape(STUDENT_NAME), meta_style))
        story.append(Paragraph(html.escape(REG_NO), meta_style))
        story.append(Paragraph(html.escape(SUBJECT), meta_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Unit 2, S{session_num}, SLO{slo_num} - {html.escape(title)}</b>", title_style))
        story.append(Spacer(1, 6))
        
        for q, a in qa_pairs:
            # Format questions and answers with html line breaks
            q_formatted = html.escape(q).replace("\n", "<br/>")
            a_formatted = html.escape(a).replace("\n", "<br/>")
            story.append(Paragraph(q_formatted, q_style))
            story.append(Paragraph(f"<b>Answer:</b> {a_formatted}", a_style))
            
        doc.build(story)
        print(f"  [OK] {pdf_path.name} ({pdf_path.stat().st_size} bytes)")


if __name__ == "__main__":
    build_docx_files()
    generate_all_pdfs()
    print("\nAll 28 Unit 2 Documents successfully generated and converted to PDF!")
