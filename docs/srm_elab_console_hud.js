/**
 * ============================================================================
 *   JARVIS X - SRM eLab CONSOLE MASTER & FLOATING HUD SUITE
 * ============================================================================
 * 
 * Instructions:
 * 1. Open SRM eLab in Chrome: https://dld.srmist.edu.in/#/fetelab/student/home
 * 2. Navigate to your assignment / question wheel.
 * 3. Press F12 (or Ctrl + Shift + I) -> Click the "Console" tab.
 * 4. Paste this ENTIRE code block into the console and hit Enter.
 * 
 * What it does:
 * - Instantly lifts ALL copy-paste, right-click, and selection restrictions.
 * - Spawns a floating, draggable Jarvis X Tactical HUD directly on the eLab tab.
 * - One-click injection of all 8 standard C solutions for Searching, Sorting, Arrays, and Linked Lists.
 * - Auto-detects the active Ace / CodeMirror / textarea editor and sets code cleanly.
 * - Auto-scrapes and displays the active question description.
 */

(function () {
    console.log("%c[JARVIS X] Initializing SRM eLab Master Suite...", "color: #00ffcc; font-weight: bold; font-size: 14px;");

    // ========================================================================
    // 1. UNLOCK CLIPBOARD & REMOVE RESTRICTIONS
    // ========================================================================
    const eventsToFree = ['copy', 'cut', 'paste', 'contextmenu', 'selectstart', 'dragstart', 'keydown', 'keypress', 'keyup'];
    eventsToFree.forEach(evt => {
        window.addEventListener(evt, e => e.stopImmediatePropagation(), true);
        document.addEventListener(evt, e => e.stopImmediatePropagation(), true);
    });
    document.oncontextmenu = null;
    document.onselectstart = null;
    document.ondragstart = null;
    document.body.style.userSelect = 'auto';
    console.log("%c[JARVIS X] âœ… Copy-Paste & Right-Click Protections Neutralized!", "color: #00ff88; font-weight: bold;");

    // ========================================================================
    // 2. EMBEDDED SOLUTIONS (All 8 C Programs across 4 Topics)
    // ========================================================================
    const SOLUTIONS = {
        "search_linear": {
            name: "Linear Search",
            topic: "Searching",
            code: `#include <stdio.h>

int main() {
    int n, key, found = 0;
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    int arr[n];
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    scanf("%d", &key);
    for (int i = 0; i < n; i++) {
        if (arr[i] == key) {
            printf("Element %d found at position %d\\n", key, i + 1);
            found = 1;
            break;
        }
    }
    if (!found) {
        printf("Element %d not found\\n", key);
    }
    return 0;
}`
        },
        "search_binary": {
            name: "Binary Search",
            topic: "Searching",
            code: `#include <stdio.h>

int binarySearch(int arr[], int n, int key) {
    int low = 0, high = n - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] == key) return mid;
        else if (arr[mid] < key) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}

int main() {
    int n, key;
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    int arr[n];
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    scanf("%d", &key);
    int index = binarySearch(arr, n, key);
    if (index != -1) {
        printf("Element %d found at index %d\\n", key, index);
    } else {
        printf("Element %d not found\\n", key);
    }
    return 0;
}`
        },
        "sort_bubble": {
            name: "Bubble Sort",
            topic: "Sorting",
            code: `#include <stdio.h>

void bubbleSort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        int swapped = 0;
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                swapped = 1;
            }
        }
        if (!swapped) break;
    }
}

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    int arr[n];
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    bubbleSort(arr, n);
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\\n");
    return 0;
}`
        },
        "sort_insertion": {
            name: "Insertion Sort",
            topic: "Sorting",
            code: `#include <stdio.h>

void insertionSort(int arr[], int n) {
    for (int i = 1; i < n; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

int main() {
    int n;
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    int arr[n];
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    insertionSort(arr, n);
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\\n");
    return 0;
}`
        },
        "array_insert_delete": {
            name: "Array Insert & Delete",
            topic: "Arrays",
            code: `#include <stdio.h>

int main() {
    int n, pos, val, del_pos;
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    int arr[100];
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    scanf("%d %d", &pos, &val);
    if (pos >= 1 && pos <= n + 1) {
        for (int i = n; i >= pos; i--) {
            arr[i] = arr[i - 1];
        }
        arr[pos - 1] = val;
        n++;
    }
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\\n");
    if (scanf("%d", &del_pos) == 1) {
        if (del_pos >= 1 && del_pos <= n) {
            for (int i = del_pos - 1; i < n - 1; i++) {
                arr[i] = arr[i + 1];
            }
            n--;
        }
        for (int i = 0; i < n; i++) {
            printf("%d ", arr[i]);
        }
        printf("\\n");
    }
    return 0;
}`
        },
        "array_rotate": {
            name: "Array Left Rotation",
            topic: "Arrays",
            code: `#include <stdio.h>

void reverse(int arr[], int start, int end) {
    while (start < end) {
        int temp = arr[start];
        arr[start++] = arr[end];
        arr[end--] = temp;
    }
}

int main() {
    int n, k;
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    int arr[n];
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    scanf("%d", &k);
    k %= n;
    reverse(arr, 0, k - 1);
    reverse(arr, k, n - 1);
    reverse(arr, 0, n - 1);
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\\n");
    return 0;
}`
        },
        "ll_operations": {
            name: "Linked List Creation & Display",
            topic: "Linked Lists",
            code: `#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node* next;
};

struct Node* insertEnd(struct Node* head, int data) {
    struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));
    newNode->data = data;
    newNode->next = NULL;
    if (head == NULL) return newNode;
    struct Node* temp = head;
    while (temp->next != NULL) {
        temp = temp->next;
    }
    temp->next = newNode;
    return head;
}

void display(struct Node* head) {
    struct Node* temp = head;
    while (temp != NULL) {
        printf("%d -> ", temp->data);
        temp = temp->next;
    }
    printf("NULL\\n");
}

int main() {
    int n, val;
    struct Node* head = NULL;
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    for (int i = 0; i < n; i++) {
        scanf("%d", &val);
        head = insertEnd(head, val);
    }
    display(head);
    return 0;
}`
        },
        "ll_reverse": {
            name: "Linked List Reversal",
            topic: "Linked Lists",
            code: `#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node* next;
};

struct Node* insertEnd(struct Node* head, int data) {
    struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));
    newNode->data = data;
    newNode->next = NULL;
    if (head == NULL) return newNode;
    struct Node* temp = head;
    while (temp->next != NULL) {
        temp = temp->next;
    }
    temp->next = newNode;
    return head;
}

struct Node* reverseList(struct Node* head) {
    struct Node *prev = NULL, *curr = head, *next = NULL;
    while (curr != NULL) {
        next = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next;
    }
    return prev;
}

void display(struct Node* head) {
    struct Node* temp = head;
    while (temp != NULL) {
        printf("%d ", temp->data);
        temp = temp->next;
    }
    printf("\\n");
}

int main() {
    int n, val;
    struct Node* head = NULL;
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    for (int i = 0; i < n; i++) {
        scanf("%d", &val);
        head = insertEnd(head, val);
    }
    head = reverseList(head);
    display(head);
    return 0;
}`
        }
    };

    // ========================================================================
    // 3. EDITOR HOOK ENGINE
    // ========================================================================
    function injectCodeToEditor(code) {
        let injected = false;

        // Method A: Ace Editor via DOM env
        const aceEls = document.querySelectorAll('.ace_editor');
        for (const el of aceEls) {
            if (el.env && el.env.editor) {
                el.env.editor.setValue(code, 1);
                injected = true;
                break;
            }
        }

        // Method B: window.ace global
        if (!injected && window.ace && typeof window.ace.edit === 'function') {
            try {
                const target = document.querySelector('.ace_editor') || document.querySelector('#editor');
                if (target) {
                    const editor = window.ace.edit(target);
                    editor.setValue(code, 1);
                    injected = true;
                }
            } catch (e) {}
        }

        // Method C: CodeMirror
        if (!injected) {
            const cmEl = document.querySelector('.CodeMirror');
            if (cmEl && cmEl.CodeMirror) {
                cmEl.CodeMirror.setValue(code);
                injected = true;
            }
        }

        // Method D: Standard textarea / input
        if (!injected) {
            const textareas = document.querySelectorAll('textarea');
            for (const ta of textareas) {
                if (ta.offsetParent !== null) { // visible
                    ta.value = code;
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                    ta.dispatchEvent(new Event('change', { bubbles: true }));
                    injected = true;
                    break;
                }
            }
        }

        return injected;
    }

    // ========================================================================
    // 4. QUESTION SCRAPER
    // ========================================================================
    function getQuestionDetails() {
        const titleEl = document.querySelector('h3, h4, .question-title, .problem-title');
        const descEls = document.querySelectorAll('.question-description, .problem-description, .card-body, .question-body, pre');
        
        let title = titleEl ? titleEl.innerText.trim() : "Current eLab Problem";
        let desc = "";
        descEls.forEach(el => {
            if (el && el.innerText && el.innerText.trim().length > 10) {
                desc += "\n" + el.innerText.trim();
            }
        });
        return { title, desc: desc.trim() };
    }

    // ========================================================================
    // 5. FLOATING HUD OVERLAY (Jarvis X Dark Tactical)
    // ========================================================================
    const existingHud = document.getElementById('jarvisx-elab-hud');
    if (existingHud) existingHud.remove();

    const hud = document.createElement('div');
    hud.id = 'jarvisx-elab-hud';
    hud.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999999;
        width: 320px;
        background: rgba(13, 17, 23, 0.95);
        border: 1px solid #00ffcc;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 255, 204, 0.25), 0 0 15px rgba(0, 0, 0, 0.8);
        color: #f0f6fc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
        font-size: 13px;
        backdrop-filter: blur(10px);
        overflow: hidden;
        user-select: none;
    `;

    hud.innerHTML = `
        <div id="jarvisx-hud-header" style="background: linear-gradient(90deg, #002233, #004455); padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; cursor: move; border-bottom: 1px solid #00ffcc44;">
            <div style="font-weight: 800; color: #00ffcc; letter-spacing: 1px; display: flex; align-items: center; gap: 6px;">
                <span style="color: #00ff88;">âš¡</span> JARVIS X :: eLab HUD
            </div>
            <button id="jarvisx-hud-close" style="background: none; border: none; color: #8b949e; cursor: pointer; font-size: 16px; line-height: 1;">&times;</button>
        </div>
        <div style="padding: 12px;">
            <div style="display: flex; gap: 6px; margin-bottom: 10px;">
                <button id="btn-unlock" style="flex: 1; padding: 6px 8px; background: #238636; border: none; border-radius: 6px; color: #fff; font-weight: 600; cursor: pointer; font-size: 11px;">ðŸ”“ Unlocked</button>
                <button id="btn-inspect" style="flex: 1; padding: 6px 8px; background: #1f6feb; border: none; border-radius: 6px; color: #fff; font-weight: 600; cursor: pointer; font-size: 11px;">ðŸ” Read Prompt</button>
            </div>

            <div style="font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: bold;">Quick Solution Injector:</div>
            <select id="jarvisx-solution-select" style="width: 100%; padding: 7px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #58a6ff; font-size: 12px; margin-bottom: 8px; outline: none;">
                <optgroup label="Searching">
                    <option value="search_linear">â–¶ 1. Linear Search</option>
                    <option value="search_binary">â–¶ 2. Binary Search</option>
                </optgroup>
                <optgroup label="Sorting">
                    <option value="sort_bubble">â–¶ 3. Bubble Sort</option>
                    <option value="sort_insertion">â–¶ 4. Insertion Sort</option>
                </optgroup>
                <optgroup label="Arrays">
                    <option value="array_insert_delete">â–¶ 5. Array Insert & Delete</option>
                    <option value="array_rotate">â–¶ 6. Array Left Rotation</option>
                </optgroup>
                <optgroup label="Linked Lists">
                    <option value="ll_operations">â–¶ 7. Linked List Creation & Display</option>
                    <option value="ll_reverse">â–¶ 8. Linked List Reversal</option>
                </optgroup>
            </select>

            <button id="btn-inject" style="width: 100%; padding: 8px; background: linear-gradient(135deg, #00ffcc, #0088ff); border: none; border-radius: 6px; color: #000; font-weight: 800; cursor: pointer; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                âš¡ Inject Selected Code
            </button>

            <div id="jarvisx-status" style="padding: 6px; background: #161b22; border-radius: 6px; font-size: 11px; color: #7ee787; text-align: center;">
                Status: Ready for Injection
            </div>
        </div>
    `;

    document.body.appendChild(hud);

    // Draggable header
    const header = document.getElementById('jarvisx-hud-header');
    let isDragging = false, startX, startY, initialLeft, initialTop;
    header.onmousedown = function (e) {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        const rect = hud.getBoundingClientRect();
        initialLeft = rect.left;
        initialTop = rect.top;
        document.onmousemove = function (e) {
            if (!isDragging) return;
            hud.style.left = (initialLeft + e.clientX - startX) + 'px';
            hud.style.top = (initialTop + e.clientY - startY) + 'px';
            hud.style.right = 'auto';
        };
        document.onmouseup = function () {
            isDragging = false;
            document.onmousemove = null;
            document.onmouseup = null;
        };
    };

    // Event handlers
    document.getElementById('jarvisx-hud-close').onclick = () => hud.remove();
    
    document.getElementById('btn-unlock').onclick = () => {
        eventsToFree.forEach(evt => {
            window.addEventListener(evt, e => e.stopImmediatePropagation(), true);
            document.addEventListener(evt, e => e.stopImmediatePropagation(), true);
        });
        const status = document.getElementById('jarvisx-status');
        status.style.color = '#7ee787';
        status.innerText = "âœ… Paste Re-Unlocked!";
    };

    document.getElementById('btn-inspect').onclick = () => {
        const info = getQuestionDetails();
        console.log("%c[JARVIS X - QUESTION DETECTED]", "color: #58a6ff; font-weight: bold;", info);
        const status = document.getElementById('jarvisx-status');
        status.style.color = '#58a6ff';
        status.innerText = `ðŸ“‹ Found: ${info.title.slice(0, 24)}...`;
        alert(`[eLab Question Detected]\n\nTitle: ${info.title}\n\nCheck Console (F12) for full details!`);
    };

    document.getElementById('btn-inject').onclick = () => {
        const select = document.getElementById('jarvisx-solution-select');
        const key = select.value;
        const item = SOLUTIONS[key];
        const status = document.getElementById('jarvisx-status');

        if (!item) return;

        const success = injectCodeToEditor(item.code);
        if (success) {
            status.style.color = '#7ee787';
            status.innerText = `âœ… Injected: ${item.name}!`;
            console.log(`%c[JARVIS X] Successfully injected ${item.name} into editor!`, "color: #00ff88; font-weight: bold;");
        } else {
            // Fallback: Copy to clipboard so user can press Ctrl+V
            navigator.clipboard.writeText(item.code);
            status.style.color = '#ffa657';
            status.innerText = `âš ï¸ Copied to clipboard! Press Ctrl+V`;
            console.log(`%c[JARVIS X] Editor handle not found. Code copied to clipboard! Press Ctrl+V into the editor.`, "color: #ffa657; font-weight: bold;");
        }
    };

    // ========================================================================
    // 6. GLOBAL CONSOLE API (For direct typing in console)
    // ========================================================================
    window.jarvis = {
        unlock: () => {
            document.getElementById('btn-unlock').click();
        },
        inject: (keyOrIndex) => {
            const keys = Object.keys(SOLUTIONS);
            let targetKey = keyOrIndex;
            if (typeof keyOrIndex === 'number' && keyOrIndex >= 1 && keyOrIndex <= keys.length) {
                targetKey = keys[keyOrIndex - 1];
            }
            if (SOLUTIONS[targetKey]) {
                injectCodeToEditor(SOLUTIONS[targetKey].code);
                console.log(`%c[JARVIS X] Injected ${SOLUTIONS[targetKey].name}!`, "color: #00ff88; font-weight: bold;");
            } else {
                console.log("%c[JARVIS X] Available keys:", "color: #58a6ff;", keys);
            }
        },
        read: () => {
            const info = getQuestionDetails();
            console.log(info);
            return info;
        },
        paste: (customCode) => {
            injectCodeToEditor(customCode);
        }
    };

    console.log("%c[JARVIS X] âœ… Suite Ready! Floating HUD Active on Screen.", "color: #00ffcc; font-weight: bold; font-size: 13px;");
    console.log("%cUse 'jarvis.inject(1)' to 'jarvis.inject(8)' directly in console or use the on-screen HUD!", "color: #a5d6ff;");
})();
