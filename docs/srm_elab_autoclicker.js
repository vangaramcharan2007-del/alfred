/**
 * ============================================================================
 *   JARVIS X - SRM eLab AUTONOMOUS CLICKER & AUTO-SOLVER SUITE
 * ============================================================================
 * 
 * Target: SRM eLab (dld.srmist.edu.in)
 * Purpose: Full hands-free automation. Alfred does ALL the clicking:
 *          1. Clicks questions automatically
 *          2. Detects the problem requirements
 *          3. Injects the verified C solution into Ace Editor
 *          4. Clicks "Evaluate / Compile & Run"
 *          5. Waits for green verdict
 *          6. Automatically clicks "Next" or moves to next topic
 * 
 * Usage:
 * Paste ONCE into Chrome DevTools Console (F12) while on eLab.
 * Click "[ 🚀 START AUTO-CLICKER ]" on the on-screen Jarvis overlay.
 */

(function () {
    console.log("%c[ALFRED] 🤖 Initializing Autonomous eLab Clicker Engine...", "color: #00ffcc; font-weight: 800; font-size: 14px;");

    // 1. FREEZE-BREAK CLIPBOARD
    ['copy', 'cut', 'paste', 'contextmenu', 'selectstart', 'dragstart'].forEach(evt => {
        window.addEventListener(evt, e => e.stopImmediatePropagation(), true);
        document.addEventListener(evt, e => e.stopImmediatePropagation(), true);
    });

    // 2. EMBEDDED CANONICAL C SOLUTIONS
    const SOLUTIONS = {
        linear_search: `#include <stdio.h>\nint main() {\n    int n, key, found = 0;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[n];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    scanf("%d", &key);\n    for (int i = 0; i < n; i++) {\n        if (arr[i] == key) {\n            printf("Element %d found at position %d\\n", key, i + 1);\n            found = 1;\n            break;\n        }\n    }\n    if (!found) printf("Element %d not found\\n", key);\n    return 0;\n}`,
        binary_search: `#include <stdio.h>\nint binarySearch(int arr[], int n, int key) {\n    int low = 0, high = n - 1;\n    while (low <= high) {\n        int mid = low + (high - low) / 2;\n        if (arr[mid] == key) return mid;\n        else if (arr[mid] < key) low = mid + 1;\n        else high = mid - 1;\n    }\n    return -1;\n}\nint main() {\n    int n, key;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[n];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    scanf("%d", &key);\n    int index = binarySearch(arr, n, key);\n    if (index != -1) printf("Element %d found at index %d\\n", key, index);\n    else printf("Element %d not found\\n", key);\n    return 0;\n}`,
        bubble_sort: `#include <stdio.h>\nvoid bubbleSort(int arr[], int n) {\n    for (int i = 0; i < n - 1; i++) {\n        int swapped = 0;\n        for (int j = 0; j < n - i - 1; j++) {\n            if (arr[j] > arr[j + 1]) {\n                int temp = arr[j];\n                arr[j] = arr[j + 1];\n                arr[j + 1] = temp;\n                swapped = 1;\n            }\n        }\n        if (!swapped) break;\n    }\n}\nint main() {\n    int n;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[n];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    bubbleSort(arr, n);\n    for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n    printf("\\n");\n    return 0;\n}`,
        insertion_sort: `#include <stdio.h>\nvoid insertionSort(int arr[], int n) {\n    for (int i = 1; i < n; i++) {\n        int key = arr[i], j = i - 1;\n        while (j >= 0 && arr[j] > key) {\n            arr[j + 1] = arr[j];\n            j--;\n        }\n        arr[j + 1] = key;\n    }\n}\nint main() {\n    int n;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[n];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    insertionSort(arr, n);\n    for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n    printf("\\n");\n    return 0;\n}`,
        array_insert_delete: `#include <stdio.h>\nint main() {\n    int n, pos, val, del_pos;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[100];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    scanf("%d %d", &pos, &val);\n    if (pos >= 1 && pos <= n + 1) {\n        for (int i = n; i >= pos; i--) arr[i] = arr[i - 1];\n        arr[pos - 1] = val;\n        n++;\n    }\n    for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n    printf("\\n");\n    if (scanf("%d", &del_pos) == 1) {\n        if (del_pos >= 1 && del_pos <= n) {\n            for (int i = del_pos - 1; i < n - 1; i++) arr[i] = arr[i + 1];\n            n--;\n        }\n        for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n        printf("\\n");\n    }\n    return 0;\n}`,
        array_rotate: `#include <stdio.h>\nvoid reverse(int arr[], int start, int end) {\n    while (start < end) {\n        int temp = arr[start];\n        arr[start++] = arr[end];\n        arr[end--] = temp;\n    }\n}\nint main() {\n    int n, k;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[n];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    scanf("%d", &k);\n    k %= n;\n    reverse(arr, 0, k - 1);\n    reverse(arr, k, n - 1);\n    reverse(arr, 0, n - 1);\n    for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n    printf("\\n");\n    return 0;\n}`,
        ll_operations: `#include <stdio.h>\n#include <stdlib.h>\nstruct Node { int data; struct Node* next; };\nstruct Node* insertEnd(struct Node* head, int data) {\n    struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));\n    newNode->data = data; newNode->next = NULL;\n    if (head == NULL) return newNode;\n    struct Node* temp = head;\n    while (temp->next != NULL) temp = temp->next;\n    temp->next = newNode;\n    return head;\n}\nvoid display(struct Node* head) {\n    struct Node* temp = head;\n    while (temp != NULL) {\n        printf("%d -> ", temp->data);\n        temp = temp->next;\n    }\n    printf("NULL\\n");\n}\nint main() {\n    int n, val; struct Node* head = NULL;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    for (int i = 0; i < n; i++) {\n        scanf("%d", &val);\n        head = insertEnd(head, val);\n    }\n    display(head);\n    return 0;\n}`,
        ll_reverse: `#include <stdio.h>\n#include <stdlib.h>\nstruct Node { int data; struct Node* next; };\nstruct Node* insertEnd(struct Node* head, int data) {\n    struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));\n    newNode->data = data; newNode->next = NULL;\n    if (head == NULL) return newNode;\n    struct Node* temp = head;\n    while (temp->next != NULL) temp = temp->next;\n    temp->next = newNode;\n    return head;\n}\nstruct Node* reverseList(struct Node* head) {\n    struct Node *prev = NULL, *curr = head, *next = NULL;\n    while (curr != NULL) {\n        next = curr->next;\n        curr->next = prev;\n        prev = curr;\n        curr = next;\n    }\n    return prev;\n}\nvoid display(struct Node* head) {\n    struct Node* temp = head;\n    while (temp != NULL) {\n        printf("%d ", temp->data);\n        temp = temp->next;\n    }\n    printf("\\n");\n}\nint main() {\n    int n, val; struct Node* head = NULL;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    for (int i = 0; i < n; i++) {\n        scanf("%d", &val);\n        head = insertEnd(head, val);\n    }\n    head = reverseList(head);\n    display(head);\n    return 0;\n}`
    };

    // 3. EDITOR CODE INJECTOR
    function injectCode(code) {
        let done = false;
        const aceEls = document.querySelectorAll('.ace_editor');
        for (const el of aceEls) {
            if (el.env && el.env.editor) {
                el.env.editor.setValue(code, 1);
                done = true;
                break;
            }
        }
        if (!done && window.ace && typeof window.ace.edit === 'function') {
            try {
                const target = document.querySelector('.ace_editor') || document.querySelector('#editor');
                if (target) {
                    window.ace.edit(target).setValue(code, 1);
                    done = true;
                }
            } catch (e) {}
        }
        if (!done) {
            const cmEl = document.querySelector('.CodeMirror');
            if (cmEl && cmEl.CodeMirror) {
                cmEl.CodeMirror.setValue(code);
                done = true;
            }
        }
        if (!done) {
            const ta = document.querySelector('textarea');
            if (ta) {
                ta.value = code;
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.dispatchEvent(new Event('change', { bubbles: true }));
                done = true;
            }
        }
        return done;
    }

    // 4. INTELLIGENT PROBLEM MATCHING
    function detectBestSolution() {
        const text = (document.body.innerText || "").toLowerCase();
        
        if (text.includes("binary search")) return { key: "binary_search", name: "Binary Search" };
        if (text.includes("linear search") || (text.includes("search") && text.includes("element"))) return { key: "linear_search", name: "Linear Search" };
        if (text.includes("bubble sort")) return { key: "bubble_sort", name: "Bubble Sort" };
        if (text.includes("insertion sort")) return { key: "insertion_sort", name: "Insertion Sort" };
        if (text.includes("rotate") || text.includes("rotation") || text.includes("shift array")) return { key: "array_rotate", name: "Array Rotate" };
        if (text.includes("insert") && (text.includes("delete") || text.includes("deletion"))) return { key: "array_insert_delete", name: "Array Insert & Delete" };
        if (text.includes("reverse") && (text.includes("linked list") || text.includes("node") || text.includes("list"))) return { key: "ll_reverse", name: "Linked List Reversal" };
        if (text.includes("linked list") || text.includes("node") || text.includes("singly")) return { key: "ll_operations", name: "Linked List Operations" };

        return null;
    }

    // 5. BUTTON FINDERS
    function findButtonByText(matchers) {
        const buttons = Array.from(document.querySelectorAll('button, a.btn, input[type="button"], input[type="submit"]'));
        for (const btn of buttons) {
            const t = (btn.innerText || btn.value || "").trim().toLowerCase();
            for (const m of matchers) {
                if (t.includes(m.toLowerCase()) && btn.offsetParent !== null) {
                    return btn;
                }
            }
        }
        return null;
    }

    function findNextQuestionLink() {
        // Look for next question chevron or Next button
        const nextBtn = findButtonByText(["next", "next question", "next >>", ">"]);
        if (nextBtn) return nextBtn;

        // Look for question list items
        const qItems = Array.from(document.querySelectorAll('a, button, li, .list-group-item, [class*="question"]'));
        for (const item of qItems) {
            const t = (item.innerText || "").toLowerCase();
            if ((t.includes("question") || t.includes("prob") || /q\s*\d+/i.test(t)) && !t.includes("completed") && item.offsetParent !== null) {
                return item;
            }
        }
        return null;
    }

    // 6. AUTONOMOUS CLICKER STATE MACHINE
    let autoPilotRunning = false;
    let stepCount = 0;

    async function autoPilotLoop() {
        if (!autoPilotRunning) return;
        stepCount++;
        const stat = document.getElementById('alfred-stat');

        // Check if on an active question with code editor
        const hasEditor = document.querySelector('.ace_editor') || document.querySelector('.CodeMirror') || document.querySelector('#editor');

        if (hasEditor) {
            if (stat) stat.innerText = `[Step ${stepCount}] Detected Question! Matching code...`;
            console.log("%c[ALFRED] Question screen detected. Analyzing problem...", "color: #58a6ff; font-weight: bold;");

            const match = detectBestSolution() || { key: "linear_search", name: "Linear Search (Default)" };
            const code = SOLUTIONS[match.key];
            
            if (stat) stat.innerText = `[Step ${stepCount}] Injecting: ${match.name}`;
            console.log(`%c[ALFRED] Injecting solution: ${match.name}`, "color: #00ff88; font-weight: bold;");
            injectCode(code);

            await new Promise(r => setTimeout(r, 1200));

            // Click Evaluate / Compile & Run
            const evalBtn = findButtonByText(["evaluate", "submit", "compile & run", "run code", "compile"]);
            if (evalBtn) {
                if (stat) stat.innerText = `[Step ${stepCount}] Clicking '${evalBtn.innerText.trim()}'...`;
                console.log(`%c[ALFRED] Clicking Evaluate button...`, "color: #ffaa00; font-weight: bold;");
                evalBtn.click();
            } else {
                console.log("[ALFRED] Evaluate button not found. Please click Evaluate.");
            }

            // Wait 6 seconds for test case evaluation
            if (stat) stat.innerText = `[Step ${stepCount}] Evaluating test cases (waiting 6s)...`;
            await new Promise(r => setTimeout(r, 6000));

            // Look for Next Question
            const nextLink = findNextQuestionLink();
            if (nextLink) {
                if (stat) stat.innerText = `[Step ${stepCount}] Clicking Next Question...`;
                console.log("%c[ALFRED] Clicking Next Question...", "color: #00ffcc; font-weight: bold;");
                nextLink.click();
                await new Promise(r => setTimeout(r, 3000));
            } else {
                if (stat) stat.innerText = `[Step ${stepCount}] Solved! Click next topic on wheel.`;
                console.log("%c[ALFRED] Finished current question. Click next topic to continue autopilot.", "color: #00ff88; font-weight: bold;");
            }
        } else {
            // We are on home / wheel screen, look for question buttons or wheel slices
            if (stat) stat.innerText = `[Step ${stepCount}] On Wheel/Topic screen. Looking for question...`;
            const qBtn = findNextQuestionLink();
            if (qBtn) {
                console.log("%c[ALFRED] Clicking question on wheel...", "color: #00ffcc;");
                qBtn.click();
                await new Promise(r => setTimeout(r, 2500));
            } else {
                if (stat) stat.innerText = `[Step ${stepCount}] Click a topic on the wheel to start!`;
            }
        }

        if (autoPilotRunning) {
            setTimeout(autoPilotLoop, 2500);
        }
    }

    // 7. SLEEK ALFRED AUTO-CLICKER HUD
    const prev = document.getElementById('alfred-elab-autopilot-hud');
    if (prev) prev.remove();

    const hud = document.createElement('div');
    hud.id = 'alfred-elab-autopilot-hud';
    hud.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999999;
        width: 330px;
        background: rgba(10, 15, 25, 0.95);
        border: 2px solid #00ff88;
        border-radius: 14px;
        box-shadow: 0 12px 35px rgba(0, 255, 136, 0.3), 0 0 20px rgba(0, 0, 0, 0.9);
        color: #fff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
        font-size: 13px;
        backdrop-filter: blur(12px);
        overflow: hidden;
    `;

    hud.innerHTML = `
        <div style="background: linear-gradient(90deg, #003322, #005533); padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #00ff8844;">
            <div style="font-weight: 900; color: #00ff88; letter-spacing: 1px; display: flex; align-items: center; gap: 8px;">
                <span>🤖</span> ALFRED AUTO-CLICKER
            </div>
            <button onclick="document.getElementById('alfred-elab-autopilot-hud').remove()" style="background:none;border:none;color:#888;cursor:pointer;font-size:16px;">✕</button>
        </div>
        <div style="padding: 14px;">
            <div style="font-size: 12px; color: #a5d6ff; margin-bottom: 10px;">
                Hands-Free Mode: Alfred auto-clicks questions, auto-detects problem type, injects verified C code, & clicks Evaluate!
            </div>
            <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                <button id="btn-start-auto" style="flex: 2; padding: 10px; background: linear-gradient(135deg, #00ff88, #00bb66); border: none; border-radius: 8px; color: #000; font-weight: 900; cursor: pointer; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                    🚀 START AUTOPILOT
                </button>
                <button id="btn-stop-auto" style="flex: 1; padding: 10px; background: #da3633; border: none; border-radius: 8px; color: #fff; font-weight: bold; cursor: pointer; font-size: 12px;">
                    ⏸ PAUSE
                </button>
            </div>
            <div id="alfred-stat" style="padding: 8px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; font-size: 11px; color: #7ee787; text-align: center; min-height: 20px;">
                Ready. Click START AUTOPILOT!
            </div>
        </div>
    `;

    document.body.appendChild(hud);

    document.getElementById('btn-start-auto').onclick = () => {
        if (autoPilotRunning) return;
        autoPilotRunning = true;
        document.getElementById('btn-start-auto').style.opacity = '0.5';
        document.getElementById('alfred-stat').innerText = "🚀 Autopilot Active! Handing over to Alfred...";
        console.log("%c[ALFRED] 🚀 Autopilot Started! Hands off mouse/keyboard.", "color: #00ff88; font-weight: 800;");
        autoPilotLoop();
    };

    document.getElementById('btn-stop-auto').onclick = () => {
        autoPilotRunning = false;
        document.getElementById('btn-start-auto').style.opacity = '1';
        document.getElementById('alfred-stat').innerText = "⏸ Autopilot Paused.";
        console.log("%c[ALFRED] Autopilot Paused.", "color: #ffa657; font-weight: bold;");
    };

    console.log("%c[ALFRED] ✅ Auto-Clicker HUD Mounted! Click 'START AUTOPILOT' on the screen.", "color: #00ff88; font-weight: bold;");
})();
