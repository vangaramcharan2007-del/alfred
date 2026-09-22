/**
 * JARVIS X - 100% Solution Injector for Level 1 • Challenge 11 (Laptop / APPU Sale)
 * Injects verified C code and automatically clicks EVALUATE.
 */
(() => {
    const code = `#include <stdio.h>
#include <stdlib.h>

int cmp(const void *a, const void *b) {
    return (*(int*)a - *(int*)b);
}

int main() {
    int t;
    if (scanf("%d", &t) != 1) return 0;
    while (t--) {
        int n, m;
        if (scanf("%d %d", &n, &m) != 2) break;
        int a[n];
        for (int i = 0; i < n; i++) {
            scanf("%d", &a[i]);
        }
        qsort(a, n, sizeof(int), cmp);
        int sum = 0;
        int limit = (n < m) ? n : m;
        for (int i = 0; i < limit; i++) {
            if (a[i] < 0) {
                sum += -a[i];
            } else {
                break;
            }
        }
        printf("%d\\n", sum);
    }
    return 0;
}`;

    // 1. Inject into Ace Editor
    let injected = false;
    document.querySelectorAll('.ace_editor').forEach(el => {
        if (el.env && el.env.editor) {
            el.env.editor.setValue(code, 1);
            injected = true;
        }
    });
    if (!injected && window.ace) {
        try {
            window.ace.edit(document.querySelector('.ace_editor') || 'editor').setValue(code, 1);
            injected = true;
        } catch(e) {}
    }
    if (!injected) {
        const ta = document.querySelector('textarea');
        if (ta) {
            ta.value = code;
            ta.dispatchEvent(new Event('input', { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));
            injected = true;
        }
    }

    console.log("%c[ALFRED] ✅ Solution injected for Challenge 11!", "color:#00ff88;font-weight:bold;font-size:14px;");

    // 2. Automatically Click EVALUATE
    setTimeout(() => {
        const evalBtn = Array.from(document.querySelectorAll('button, a, input')).find(el => {
            const t = (el.innerText || el.value || "").trim().toLowerCase();
            return t === "evaluate" || t.includes("evaluate");
        });
        if (evalBtn) {
            console.log("%c[ALFRED] 🚀 Clicking EVALUATE automatically...", "color:#ffaa00;font-weight:bold;");
            evalBtn.click();
        }
    }, 600);
})();
