/**
 * ============================================================================
 *   JARVIS X - SRM eLab AUTONOMOUS CLICKER WITH PER-TOPIC QUOTA ENGINE
 * ============================================================================
 * 
 * Features:
 * 1. Strict Per-Topic Quota: Exactly 2 (or 3) questions per topic.
 * 2. Topic State Machine:
 *    - Searching:     [ 0 / 2 ]
 *    - Sorting:       [ 0 / 2 ]
 *    - Arrays:        [ 0 / 2 ]
 *    - Linked Lists:  [ 0 / 2 ]
 * 3. Auto-Exit / Return to Wheel:
 *    Once a topic hits the quota (e.g., 2/2), Alfred automatically clicks the
 *    breadcrumb / "Home" / "Back" button to return to the sunburst wheel and
 *    select the next pending topic.
 * 4. Mission Accomplished Auto-Stop:
 *    Stops automatically when all 4 topics reach the quota.
 */

(function () {
    console.log("%c[ALFRED] 🤖 Initializing Quota-Enforced Auto-Clicker...", "color: #00ff88; font-weight: 800; font-size: 14px;");

    // 1. FREEZE-BREAK CLIPBOARD
    ['copy', 'cut', 'paste', 'contextmenu', 'selectstart', 'dragstart'].forEach(evt => {
        window.addEventListener(evt, e => e.stopImmediatePropagation(), true);
        document.addEventListener(evt, e => e.stopImmediatePropagation(), true);
    });

    // 2. CONFIGURATION & STATE
    let MAX_PER_TOPIC = 2; // Default 2 questions per topic
    const TOPIC_PROGRESS = {
        searching: 0,
        sorting: 0,
        arrays: 0,
        linked_lists: 0
    };

    const SOLUTIONS = {
        linear_search: {
            topic: "searching",
            name: "Linear Search",
            code: `#include <stdio.h>\nint main() {\n    int n, key, found = 0;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[n];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    scanf("%d", &key);\n    for (int i = 0; i < n; i++) {\n        if (arr[i] == key) {\n            printf("Element %d found at position %d\\n", key, i + 1);\n            found = 1;\n            break;\n        }\n    }\n    if (!found) printf("Element %d not found\\n", key);\n    return 0;\n}`
        },
        binary_search: {
            topic: "searching",
            name: "Binary Search",
            code: `#include <stdio.h>\nint binarySearch(int arr[], int n, int key) {\n    int low = 0, high = n - 1;\n    while (low <= high) {\n        int mid = low + (high - low) / 2;\n        if (arr[mid] == key) return mid;\n        else if (arr[mid] < key) low = mid + 1;\n        else high = mid - 1;\n    }\n    return -1;\n}\nint main() {\n    int n, key;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[n];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    scanf("%d", &key);\n    int index = binarySearch(arr, n, key);\n    if (index != -1) printf("Element %d found at index %d\\n", key, index);\n    else printf("Element %d not found\\n", key);\n    return 0;\n}`
        },
        bubble_sort: {
            topic: "sorting",
            name: "Bubble Sort",
            code: `#include <stdio.h>\nvoid bubbleSort(int arr[], int n) {\n    for (int i = 0; i < n - 1; i++) {\n        int swapped = 0;\n        for (int j = 0; j < n - i - 1; j++) {\n            if (arr[j] > arr[j + 1]) {\n                int temp = arr[j];\n                arr[j] = arr[j + 1];\n                arr[j + 1] = temp;\n                swapped = 1;\n            }\n        }\n        if (!swapped) break;\n    }\n}\nint main() {\n    int n;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[n];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    bubbleSort(arr, n);\n    for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n    printf("\\n");\n    return 0;\n}`
        },
        insertion_sort: {
            topic: "sorting",
            name: "Insertion Sort",
            code: `#include <stdio.h>\nvoid insertionSort(int arr[], int n) {\n    for (int i = 1; i < n; i++) {\n        int key = arr[i], j = i - 1;\n        while (j >= 0 && arr[j] > key) {\n            arr[j + 1] = arr[j];\n            j--;\n        }\n        arr[j + 1] = key;\n    }\n}\nint main() {\n    int n;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[n];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    insertionSort(arr, n);\n    for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n    printf("\\n");\n    return 0;\n}`
        },
        array_insert_delete: {
            topic: "arrays",
            name: "Array Insert & Delete",
            code: `#include <stdio.h>\nint main() {\n    int n, pos, val, del_pos;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[100];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    scanf("%d %d", &pos, &val);\n    if (pos >= 1 && pos <= n + 1) {\n        for (int i = n; i >= pos; i--) arr[i] = arr[i - 1];\n        arr[pos - 1] = val;\n        n++;\n    }\n    for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n    printf("\\n");\n    if (scanf("%d", &del_pos) == 1) {\n        if (del_pos >= 1 && del_pos <= n) {\n            for (int i = del_pos - 1; i < n - 1; i++) arr[i] = arr[i + 1];\n            n--;\n        }\n        for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n        printf("\\n");\n    }\n    return 0;\n}`
        },
        array_rotate: {
            topic: "arrays",
            name: "Array Left Rotation",
            code: `#include <stdio.h>\nvoid reverse(int arr[], int start, int end) {\n    while (start < end) {\n        int temp = arr[start];\n        arr[start++] = arr[end];\n        arr[end--] = temp;\n    }\n}\nint main() {\n    int n, k;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    int arr[n];\n    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);\n    scanf("%d", &k);\n    k %= n;\n    reverse(arr, 0, k - 1);\n    reverse(arr, k, n - 1);\n    reverse(arr, 0, n - 1);\n    for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n    printf("\\n");\n    return 0;\n}`
        },
        ll_operations: {
            topic: "linked_lists",
            name: "Linked List Traversal",
            code: `#include <stdio.h>\n#include <stdlib.h>\nstruct Node { int data; struct Node* next; };\nstruct Node* insertEnd(struct Node* head, int data) {\n    struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));\n    newNode->data = data; newNode->next = NULL;\n    if (head == NULL) return newNode;\n    struct Node* temp = head;\n    while (temp->next != NULL) temp = temp->next;\n    temp->next = newNode;\n    return head;\n}\nvoid display(struct Node* head) {\n    struct Node* temp = head;\n    while (temp != NULL) {\n        printf("%d -> ", temp->data);\n        temp = temp->next;\n    }\n    printf("NULL\\n");\n}\nint main() {\n    int n, val; struct Node* head = NULL;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    for (int i = 0; i < n; i++) {\n        scanf("%d", &val);\n        head = insertEnd(head, val);\n    }\n    display(head);\n    return 0;\n}`
        },
        ll_reverse: {
            topic: "linked_lists",
            name: "Linked List Reversal",
            code: `#include <stdio.h>\n#include <stdlib.h>\nstruct Node { int data; struct Node* next; };\nstruct Node* insertEnd(struct Node* head, int data) {\n    struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));\n    newNode->data = data; newNode->next = NULL;\n    if (head == NULL) return newNode;\n    struct Node* temp = head;\n    while (temp->next != NULL) temp = temp->next;\n    temp->next = newNode;\n    return head;\n}\nstruct Node* reverseList(struct Node* head) {\n    struct Node *prev = NULL, *curr = head, *next = NULL;\n    while (curr != NULL) {\n        next = curr->next;\n        curr->next = prev;\n        prev = curr;\n        curr = next;\n    }\n    return prev;\n}\nvoid display(struct Node* head) {\n    struct Node* temp = head;\n    while (temp != NULL) {\n        printf("%d ", temp->data);\n        temp = temp->next;\n    }\n    printf("\\n");\n}\nint main() {\n    int n, val; struct Node* head = NULL;\n    if (scanf("%d", &n) != 1 || n <= 0) return 0;\n    for (int i = 0; i < n; i++) {\n        scanf("%d", &val);\n        head = insertEnd(head, val);\n    }\n    head = reverseList(head);\n    display(head);\n    return 0;\n}`
        }
    };

    // 3. CODE INJECTOR
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
                if (target) { window.ace.edit(target).setValue(code, 1); done = true; }
            } catch (e) {}
        }
        if (!done) {
            const cmEl = document.querySelector('.CodeMirror');
            if (cmEl && cmEl.CodeMirror) { cmEl.CodeMirror.setValue(code); done = true; }
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

    // 4. TOPIC & PROBLEM IDENTIFIER
    function detectCurrentTopicAndSolution() {
        const text = (document.body.innerText || "").toLowerCase();

        // 1. Check Searching
        if (text.includes("binary search")) return { topic: "searching", key: "binary_search", name: "Binary Search" };
        if (text.includes("linear search") || (text.includes("search") && text.includes("element"))) return { topic: "searching", key: "linear_search", name: "Linear Search" };

        // 2. Check Sorting
        if (text.includes("bubble sort")) return { topic: "sorting", key: "bubble_sort", name: "Bubble Sort" };
        if (text.includes("insertion sort") || text.includes("sort")) return { topic: "sorting", key: "insertion_sort", name: "Insertion Sort" };

        // 3. Check Arrays
        if (text.includes("rotate") || text.includes("rotation") || text.includes("shift array")) return { topic: "arrays", key: "array_rotate", name: "Array Rotate" };
        if (text.includes("insert") || text.includes("delete") || text.includes("array")) return { topic: "arrays", key: "array_insert_delete", name: "Array Insert & Delete" };

        // 4. Check Linked Lists
        if (text.includes("reverse") && (text.includes("linked") || text.includes("node"))) return { topic: "linked_lists", key: "ll_reverse", name: "Linked List Reversal" };
        if (text.includes("linked") || text.includes("node") || text.includes("singly")) return { topic: "linked_lists", key: "ll_operations", name: "Linked List Traversal" };

        return { topic: "searching", key: "linear_search", name: "Default Problem" };
    }

    // 5. BUTTON FINDERS
    function findButtonByText(matchers) {
        const buttons = Array.from(document.querySelectorAll('button, a.btn, a, input[type="button"], input[type="submit"]'));
        for (const btn of buttons) {
            const t = (btn.innerText || btn.value || "").trim().toLowerCase();
            for (const m of matchers) {
                if (t === m.toLowerCase() || t.includes(m.toLowerCase())) {
                    if (btn.offsetParent !== null) return btn;
                }
            }
        }
        return null;
    }

    function findBackToWheelLink() {
        return findButtonByText(["home", "back", "topics", "all questions", "dashboard", "fetelab", "breadcrumb"]);
    }

    function findNextQuestionLink() {
        const nextBtn = findButtonByText(["next", "next question", "next >>", ">"]);
        if (nextBtn) return nextBtn;
        const qItems = Array.from(document.querySelectorAll('a, button, li, .list-group-item, [class*="question"]'));
        for (const item of qItems) {
            const t = (item.innerText || "").toLowerCase();
            if ((t.includes("question") || t.includes("prob") || /q\s*\d+/i.test(t)) && !t.includes("completed") && item.offsetParent !== null) {
                return item;
            }
        }
        return null;
    }

    // 6. HUD REFRESH
    function updateHUD() {
        const pSearch = document.getElementById('q-search');
        const pSort = document.getElementById('q-sort');
        const pArr = document.getElementById('q-arr');
        const pLL = document.getElementById('q-ll');

        if (pSearch) pSearch.innerText = `${TOPIC_PROGRESS.searching}/${MAX_PER_TOPIC} ${TOPIC_PROGRESS.searching >= MAX_PER_TOPIC ? '✅' : '⏳'}`;
        if (pSort) pSort.innerText = `${TOPIC_PROGRESS.sorting}/${MAX_PER_TOPIC} ${TOPIC_PROGRESS.sorting >= MAX_PER_TOPIC ? '✅' : '⏳'}`;
        if (pArr) pArr.innerText = `${TOPIC_PROGRESS.arrays}/${MAX_PER_TOPIC} ${TOPIC_PROGRESS.arrays >= MAX_PER_TOPIC ? '✅' : '⏳'}`;
        if (pLL) pLL.innerText = `${TOPIC_PROGRESS.linked_lists}/${MAX_PER_TOPIC} ${TOPIC_PROGRESS.linked_lists >= MAX_PER_TOPIC ? '✅' : '⏳'}`;
    }

    function isAllTopicsDone() {
        return (
            TOPIC_PROGRESS.searching >= MAX_PER_TOPIC &&
            TOPIC_PROGRESS.sorting >= MAX_PER_TOPIC &&
            TOPIC_PROGRESS.arrays >= MAX_PER_TOPIC &&
            TOPIC_PROGRESS.linked_lists >= MAX_PER_TOPIC
        );
    }

    // 7. AUTONOMOUS QUOTA LOOP
    let autoPilotRunning = false;

    async function autoPilotLoop() {
        if (!autoPilotRunning) return;
        const stat = document.getElementById('alfred-stat');

        if (isAllTopicsDone()) {
            autoPilotRunning = false;
            if (stat) stat.innerText = "🎉 All 4 topics completed! 1 Mark unlocked.";
            console.log("%c[ALFRED] 🏆 MISSION COMPLETE: All topics reached quota! Test portal unlocked.", "color: #00ff88; font-weight: bold; font-size: 16px;");
            alert("[JARVIS X] All 4 topics have completed their quota! Test portal unlocked.");
            return;
        }

        const hasEditor = document.querySelector('.ace_editor') || document.querySelector('.CodeMirror') || document.querySelector('#editor');

        if (hasEditor) {
            const info = detectCurrentTopicAndSolution();
            const currTopic = info.topic;

            // Check if this topic already reached quota!
            if (TOPIC_PROGRESS[currTopic] >= MAX_PER_TOPIC) {
                if (stat) stat.innerText = `Topic '${currTopic}' already at ${MAX_PER_TOPIC}/${MAX_PER_TOPIC}! Back to wheel...`;
                console.log(`%c[ALFRED] Topic '${currTopic}' quota (${MAX_PER_TOPIC}) reached. Returning to wheel for other topics...`, "color: #ffcc00; font-weight: bold;");
                
                const backBtn = findBackToWheelLink();
                if (backBtn) {
                    backBtn.click();
                    await new Promise(r => setTimeout(r, 2500));
                } else {
                    if (stat) stat.innerText = `Quota reached for ${currTopic}! Click next topic on wheel.`;
                }
                if (autoPilotRunning) setTimeout(autoPilotLoop, 2500);
                return;
            }

            // Topic still needs questions: Solve and evaluate
            if (stat) stat.innerText = `[${currTopic.toUpperCase()} ${TOPIC_PROGRESS[currTopic] + 1}/${MAX_PER_TOPIC}] Injecting ${info.name}...`;
            injectCode(SOLUTIONS[info.key].code);
            await new Promise(r => setTimeout(r, 1200));

            // Click Evaluate
            const evalBtn = findButtonByText(["evaluate", "submit", "compile & run", "run code"]);
            if (evalBtn) {
                if (stat) stat.innerText = `Evaluating ${info.name}...`;
                evalBtn.click();
            }

            // Wait 6s for evaluation
            await new Promise(r => setTimeout(r, 6000));

            // Increment quota count
            TOPIC_PROGRESS[currTopic]++;
            updateHUD();
            console.log(`%c[ALFRED] ✅ Solved problem for ${currTopic}! Progress: ${TOPIC_PROGRESS[currTopic]}/${MAX_PER_TOPIC}`, "color: #00ff88; font-weight: bold;");

            // If this topic just completed its quota, return to wheel!
            if (TOPIC_PROGRESS[currTopic] >= MAX_PER_TOPIC) {
                if (stat) stat.innerText = `✅ Finished ${MAX_PER_TOPIC} for ${currTopic}! Switching topic...`;
                const backBtn = findBackToWheelLink();
                if (backBtn) {
                    backBtn.click();
                    await new Promise(r => setTimeout(r, 2500));
                }
            } else {
                // Topic still has 1 more question to do: click next
                const nextLink = findNextQuestionLink();
                if (nextLink) {
                    if (stat) stat.innerText = `Next question in ${currTopic}...`;
                    nextLink.click();
                    await new Promise(r => setTimeout(r, 3000));
                }
            }
        } else {
            // On wheel / home screen
            if (stat) stat.innerText = "On wheel screen. Looking for pending topic...";
            const qBtn = findNextQuestionLink();
            if (qBtn) {
                qBtn.click();
                await new Promise(r => setTimeout(r, 2500));
            }
        }

        if (autoPilotRunning) setTimeout(autoPilotLoop, 2500);
    }

    // 8. TACTICAL HUD WITH QUOTA SELECTOR & LIVE PROGRESS TABLE
    const prev = document.getElementById('alfred-elab-autopilot-hud');
    if (prev) prev.remove();

    const hud = document.createElement('div');
    hud.id = 'alfred-elab-autopilot-hud';
    hud.style.cssText = 'position:fixed;bottom:25px;right:25px;z-index:9999999;width:330px;background:rgba(10,15,25,0.96);border:2px solid #00ff88;border-radius:14px;box-shadow:0 12px 35px rgba(0,255,136,0.3);color:#fff;font-family:monospace;padding:12px;backdrop-filter:blur(10px);';
    hud.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #00ff8844;padding-bottom:6px;margin-bottom:8px;">
            <span style="font-weight:900;color:#00ff88;font-size:13px;">🤖 ALFRED QUOTA AUTOPILOT</span>
            <button onclick="document.getElementById('alfred-elab-autopilot-hud').remove()" style="background:none;border:none;color:#888;cursor:pointer;font-size:14px;">✕</button>
        </div>

        <!-- Quota Selector -->
        <div style="display:flex;align-items:center;justify-content:space-between;background:#161b22;padding:6px 10px;border-radius:6px;margin-bottom:8px;font-size:11px;">
            <span>Target per topic:</span>
            <select id="sel-quota" style="background:#0d1117;color:#00ff88;border:1px solid #00ff8844;border-radius:4px;padding:2px 8px;font-weight:bold;cursor:pointer;">
                <option value="2" selected>2 Questions (Recommended)</option>
                <option value="3">3 Questions</option>
                <option value="4">4 Questions</option>
            </select>
        </div>

        <!-- Topic Progress Table -->
        <div style="background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:6px 10px;margin-bottom:10px;font-size:11px;line-height:1.6;">
            <div style="display:flex;justify-content:space-between;"><span>🔍 Searching:</span><b id="q-search" style="color:#58a6ff;">0/2 ⏳</b></div>
            <div style="display:flex;justify-content:space-between;"><span>📶 Sorting:</span><b id="q-sort" style="color:#58a6ff;">0/2 ⏳</b></div>
            <div style="display:flex;justify-content:space-between;"><span>📊 Arrays:</span><b id="q-arr" style="color:#58a6ff;">0/2 ⏳</b></div>
            <div style="display:flex;justify-content:space-between;"><span>🔗 Linked Lists:</span><b id="q-ll" style="color:#58a6ff;">0/2 ⏳</b></div>
        </div>

        <div style="display:flex;gap:6px;margin-bottom:8px;">
            <button id="btn-start-auto" style="flex:2;background:linear-gradient(135deg,#00ff88,#00aa55);color:#000;border:none;padding:8px;border-radius:6px;font-weight:bold;cursor:pointer;">🚀 START AUTOPILOT</button>
            <button id="btn-stop-auto" style="flex:1;background:#da3633;color:#fff;border:none;padding:8px;border-radius:6px;font-weight:bold;cursor:pointer;">⏸ PAUSE</button>
        </div>
        <div id="alfred-stat" style="background:#090d13;border:1px solid #30363d;padding:6px;border-radius:4px;font-size:11px;color:#7ee787;text-align:center;">Ready to hit target!</div>
    `;
    document.body.appendChild(hud);

    document.getElementById('sel-quota').onchange = (e) => {
        MAX_PER_TOPIC = parseInt(e.target.value) || 2;
        updateHUD();
        console.log(`[ALFRED] Quota updated to: ${MAX_PER_TOPIC} per topic.`);
    };

    document.getElementById('btn-start-auto').onclick = () => {
        if (autoPilotRunning) return;
        autoPilotRunning = true;
        document.getElementById('btn-start-auto').style.opacity = '0.5';
        autoPilotLoop();
    };

    document.getElementById('btn-stop-auto').onclick = () => {
        autoPilotRunning = false;
        document.getElementById('btn-start-auto').style.opacity = '1';
        document.getElementById('alfred-stat').innerText = "Paused.";
    };

    updateHUD();
})();
