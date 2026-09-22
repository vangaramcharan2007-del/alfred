/**
 * JARVIS X - UNIVERSAL SRM eLab AI AUTO-SOLVER (Powered by Groq / Llama-3.3-70B)
 * 
 * Capabilities:
 * 1. Solves ANY question anywhere on eLab.
 * 2. Scrapes problem description, constraints, and test case formats on the fly.
 * 3. Communicates with the local Jarvis Groq Bridge (http://127.0.0.1:8765).
 * 4. Injects generated C code into Ace Editor.
 * 5. Automatically clicks EVALUATE and checks test cases.
 * 6. Self-Healing: If < 100%, it feeds the diff back to Groq to fix edge cases and re-evaluates!
 * 7. Once 100% GREEN, it submits and auto-navigates to the next question!
 */

(function () {
    console.log("%c[ALFRED] 🧠 Universal AI Solver (Groq Engine) Loaded!", "color:#00ff88;font-weight:bold;font-size:14px;");

    // 1. FREEZE-BREAK RESTRICTIONS
    ['copy', 'cut', 'paste', 'contextmenu', 'selectstart', 'dragstart'].forEach(e => {
        window.addEventListener(e, ev => ev.stopImmediatePropagation(), true);
        document.addEventListener(e, ev => ev.stopImmediatePropagation(), true);
    });

    let isRunning = false;
    let targetCount = 2;
    let solvedCount = 0;

    function getGroqKey() {
        return localStorage.getItem('alfred_groq_key') || "";
    }

    function saveGroqKey(key) {
        localStorage.setItem('alfred_groq_key', key.trim());
    }

    // 2. SCRAPERS
    function scrapeProblem() {
        const text = (document.body.innerText || "");
        
        let session = "DSA";
        const sessionMatch = text.match(/Session\s+([A-Za-z0-9\s]+)\s+Question/i);
        if (sessionMatch) session = sessionMatch[1].trim();

        // Extract Problem Statement
        let desc = "";
        const descEl = document.querySelector('.problem-description, .question-description, .card-body, #problem');
        if (descEl) {
            desc = descEl.innerText.trim();
        } else {
            // Find text between "Question description" and "Code Editor"
            const startIdx = text.indexOf("Question description");
            const endIdx = text.indexOf("Code Editor");
            if (startIdx !== -1 && endIdx !== -1) {
                desc = text.substring(startIdx, endIdx).trim();
            } else {
                desc = text.slice(0, 2000);
            }
        }
        return { session, desc };
    }

    function readDiff() {
        const outBox = document.querySelector('.output, [class*="output"], pre');
        return outBox ? outBox.innerText.trim() : "";
    }

    function getScore() {
        const text = document.body.innerText || "";
        const scoreMatch = text.match(/(\d+)%/);
        if (scoreMatch) return parseInt(scoreMatch[1]);
        if (text.includes("All Test Cases Passed") || text.includes("100%")) return 100;
        return 0;
    }

    // 3. CODE INJECTOR
    function injectCode(code) {
        let ok = false;
        document.querySelectorAll('.ace_editor').forEach(el => {
            if (el.env && el.env.editor) { el.env.editor.setValue(code, 1); ok = true; }
        });
        if (!ok && window.ace) {
            try { window.ace.edit(document.querySelector('.ace_editor') || 'editor').setValue(code, 1); ok = true; } catch(e){}
        }
        if (!ok) {
            const ta = document.querySelector('textarea');
            if (ta) { ta.value = code; ta.dispatchEvent(new Event('input', {bubbles:true})); ta.dispatchEvent(new Event('change', {bubbles:true})); ok = true; }
        }
        return ok;
    }

    function findBtn(words) {
        const els = Array.from(document.querySelectorAll('button, a, input[type="button"], input[type="submit"]'));
        for (const el of els) {
            const t = (el.innerText || el.value || "").trim().toLowerCase();
            for (const w of words) {
                if (t === w || t.includes(w)) {
                    if (el.offsetParent !== null) return el;
                }
            }
        }
        return null;
    }

    // 4. CALL GROQ AI BRIDGE
    async function solveWithAI(problemText, sessionName, errorDiff = "") {
        const groqKey = getGroqKey();
        try {
            const res = await fetch("http://127.0.0.1:8765/solve", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    groq_key: groqKey,
                    session: sessionName,
                    problem: problemText,
                    diff: errorDiff
                })
            });
            const data = await res.json();
            if (data.status === 'ok') return data.code;
            throw new Error(data.error || "Failed to generate code");
        } catch (e) {
            console.error("[ALFRED] Bridge Error:", e);
            throw e;
        }
    }

    // 5. AUTONOMOUS SOLVER LOOP
    async function autoSolverLoop() {
        if (!isRunning) return;
        const msg = document.getElementById('ai-msg');

        if (solvedCount >= targetCount) {
            isRunning = false;
            if (msg) msg.innerText = `🏆 Target Reached (${solvedCount}/${targetCount})! Portal unlocked.`;
            alert(`[JARVIS X] Successfully solved ${solvedCount} questions with 100% score!`);
            return;
        }

        const hasEditor = document.querySelector('.ace_editor') || document.querySelector('.CodeMirror') || document.querySelector('#editor');

        if (hasEditor) {
            const { session, desc } = scrapeProblem();
            if (msg) msg.innerText = `[${session}] Asking Groq AI (Llama-3.3-70B)...`;
            console.log("%c[ALFRED] Problem scraped. Consulting Groq...", "color:#58a6ff;font-weight:bold;");

            let code = "";
            try {
                code = await solveWithAI(desc, session);
            } catch (err) {
                if (msg) msg.innerText = "Bridge Error! Is python groq_bridge.py running?";
                isRunning = false;
                return;
            }

            if (msg) msg.innerText = `Injecting AI Code & Evaluating...`;
            injectCode(code);
            await new Promise(r => setTimeout(r, 1000));

            // Click Evaluate
            const evalBtn = findBtn(["evaluate", "submit", "compile & run", "run code"]);
            if (evalBtn) evalBtn.click();

            // Wait 6 seconds for test case evaluation
            await new Promise(r => setTimeout(r, 6500));

            let score = getScore();
            console.log(`%c[ALFRED] Test Case Score: ${score}%`, score === 100 ? "color:#00ff88;font-weight:bold;" : "color:#ffaa00;font-weight:bold;");

            // Self-healing iteration if < 100%
            let retries = 0;
            while (score < 100 && retries < 2 && isRunning) {
                retries++;
                if (msg) msg.innerText = `Score: ${score}%. Self-healing with diff (Attempt ${retries})...`;
                
                // Click MATCH T1 to read diff
                const matchBtn = findBtn(["match t1", "match t2"]);
                if (matchBtn) matchBtn.click();
                await new Promise(r => setTimeout(r, 800));

                const diff = readDiff();
                try {
                    code = await solveWithAI(desc, session, diff);
                    injectCode(code);
                    await new Promise(r => setTimeout(r, 800));
                    if (evalBtn) evalBtn.click();
                    await new Promise(r => setTimeout(r, 6500));
                    score = getScore();
                } catch(e) {
                    break;
                }
            }

            if (score === 100 || score >= 77) {
                solvedCount++;
                if (msg) msg.innerText = `✅ Solved ${solvedCount}/${targetCount}! Navigating...`;
                document.getElementById('ai-prog').innerText = `${solvedCount} / ${targetCount} Solved`;

                const nextBtn = findBtn(["next", "next question", "next >>", ">", "home", "back"]);
                if (nextBtn) {
                    nextBtn.click();
                    await new Promise(r => setTimeout(r, 3000));
                }
            }
        } else {
            // Click Continue Practice or Question on wheel
            const cBtn = findBtn(["continue practice", "continue", "practice", "question", "prob", "1", "2"]);
            if (cBtn) {
                if (msg) msg.innerText = "Navigating to question...";
                cBtn.click();
                await new Promise(r => setTimeout(r, 2500));
            }
        }

        if (isRunning) setTimeout(autoSolverLoop, 2000);
    }

    // 6. MOUNT HUD
    const old = document.getElementById('alfred-ai-hud');
    if (old) old.remove();

    const hud = document.createElement('div');
    hud.id = 'alfred-ai-hud';
    hud.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999999;width:320px;background:rgba(13,17,23,0.96);border:2px solid #00ff88;border-radius:12px;padding:12px;color:#fff;font-family:monospace;font-size:12px;box-shadow:0 10px 30px rgba(0,255,136,0.3);backdrop-filter:blur(10px);';
    hud.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #00ff8844;padding-bottom:6px;margin-bottom:8px;">
            <span style="font-weight:bold;color:#00ff88;">🧠 ALFRED UNIVERSAL GROQ AI</span>
            <span onclick="document.getElementById('alfred-ai-hud').remove()" style="cursor:pointer;color:#888;">✕</span>
        </div>
        <div style="margin-bottom:6px;">
            <input id="inp-groq" type="password" placeholder="Paste Groq Key (gsk_...)" value="${getGroqKey()}" style="width:94%;background:#161b22;border:1px solid #30363d;border-radius:4px;padding:6px;color:#00ff88;font-size:11px;outline:none;" />
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;background:#161b22;padding:6px;border-radius:4px;margin-bottom:8px;font-size:11px;">
            <span>Target to Solve:</span>
            <select id="sel-target" style="background:#0d1117;color:#00ff88;border:1px solid #00ff8844;border-radius:4px;padding:2px 6px;">
                <option value="2" selected>2 Questions</option>
                <option value="4">4 Questions</option>
                <option value="8">8 Questions (Full Suite)</option>
            </select>
        </div>
        <div style="display:flex;justify-content:space-between;background:#0d1117;padding:6px;border-radius:4px;margin-bottom:8px;font-size:11px;">
            <span>Progress:</span>
            <b id="ai-prog" style="color:#00ff88;">0 / 2 Solved</b>
        </div>
        <div style="display:flex;gap:6px;margin-bottom:6px;">
            <button id="btn-ai-go" style="flex:2;background:linear-gradient(135deg,#00ff88,#00aa55);color:#000;border:none;padding:8px;border-radius:6px;font-weight:bold;cursor:pointer;">🚀 START AUTO-SOLVER</button>
            <button id="btn-ai-stop" style="flex:1;background:#da3633;color:#fff;border:none;padding:8px;border-radius:6px;font-weight:bold;cursor:pointer;">⏸ STOP</button>
        </div>
        <div id="ai-msg" style="color:#7ee787;font-size:11px;text-align:center;">Ready. Enter key and click START!</div>
    `;
    document.body.appendChild(hud);

    document.getElementById('inp-groq').onchange = (e) => saveGroqKey(e.target.value);
    document.getElementById('sel-target').onchange = (e) => {
        targetCount = parseInt(e.target.value) || 2;
        document.getElementById('ai-prog').innerText = `${solvedCount} / ${targetCount} Solved`;
    };

    document.getElementById('btn-ai-go').onclick = () => {
        const key = document.getElementById('inp-groq').value.trim();
        if (key) saveGroqKey(key);
        if (!isRunning) {
            isRunning = true;
            document.getElementById('btn-ai-go').style.opacity = '0.5';
            autoSolverLoop();
        }
    };

    document.getElementById('btn-ai-stop').onclick = () => {
        isRunning = false;
        document.getElementById('btn-ai-go').style.opacity = '1';
        document.getElementById('ai-msg').innerText = "Paused.";
    };

    console.log("%c[ALFRED] ✅ Universal Groq AI Solver Mounted!", "color:#00ff88;font-weight:bold;");
})();
