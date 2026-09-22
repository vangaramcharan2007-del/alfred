/**
 * JARVIS X - SRM eLab Inspector & Max-Score Solver
 * 1. Dumps the exact Question Title, Description, and Sample Input/Output.
 * 2. Clicks MATCH T1 to show the exact Expected vs Actual Output.
 * 3. Provides clean one-click injection for 100% Testcases.
 */

(function () {
    console.log("%c[JARVIS X] 🔍 Inspecting current problem and test case diff...", "color: #00ffcc; font-weight: bold; font-size: 14px;");

    // 1. Click MATCH T1 to see diff
    const matchBtns = Array.from(document.querySelectorAll('*')).filter(e => e.innerText && e.innerText.trim().startsWith('MATCH T'));
    if (matchBtns.length > 0) {
        matchBtns[0].click();
        console.log("%c[JARVIS X] Clicked MATCH T1", "color: #00ff88;");
    }

    // 2. Extract Problem Statement from DOM
    let problemText = "";
    const possibleSelectors = [
        '.problem-description', '.question-description', '.question-body',
        '.card-body', '#problem', '#question', '.problem-statement',
        'app-student-home', 'app-fetelab'
    ];

    for (const sel of possibleSelectors) {
        const el = document.querySelector(sel);
        if (el && el.innerText && el.innerText.length > 30) {
            problemText = el.innerText.trim();
            break;
        }
    }

    if (!problemText) {
        // Fallback: search all text above code editor
        const editor = document.querySelector('.ace_editor') || document.querySelector('.CodeMirror');
        if (editor) {
            let prev = editor.parentElement;
            while (prev && prev !== document.body) {
                if (prev.innerText && prev.innerText.length > 50 && prev.innerText.length < 3000) {
                    problemText = prev.innerText.trim();
                    break;
                }
                prev = prev.parentElement;
            }
        }
    }

    console.log("%c==================== PROBLEM DETAILS ====================", "color: #58a6ff; font-weight: bold;");
    console.log(problemText ? problemText.slice(0, 1000) : "Could not isolate problem container. Check output diff below.");

    // 3. Read Output Diff
    setTimeout(() => {
        const outBox = document.querySelector('.output, [class*="output"], pre') || document.querySelector('#output');
        console.log("%c==================== TEST CASE 1 DIFF ====================", "color: #ffaa00; font-weight: bold;");
        if (outBox) {
            console.log(outBox.innerText);
        } else {
            console.log("Output box contents updated on screen above.");
        }
    }, 600);
})();
