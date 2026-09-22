/**
 * JARVIS X - SRM eLab One-Click Autopilot
 * Clean, compact, zero-truncation version
 */
(function() {
    console.log("%c[ALFRED] 🤖 Autopilot Starting...", "color:#00ff88;font-weight:bold;font-size:14px;");

    // 1. Kill restrictions
    ['copy','cut','paste','contextmenu','selectstart','dragstart'].forEach(e => {
        window.addEventListener(e, ev => ev.stopImmediatePropagation(), true);
        document.addEventListener(e, ev => ev.stopImmediatePropagation(), true);
    });

    const MAX_PER_TOPIC = 2;
    const COUNTS = { searching: 0, sorting: 0, arrays: 0, linked_lists: 0 };

    const CODE = {
        linear_search: `#include <stdio.h>\nint main(){int n,k,f=0;if(scanf("%d",&n)!=1||n<=0)return 0;int a[n];for(int i=0;i<n;i++)scanf("%d",&a[i]);scanf("%d",&k);for(int i=0;i<n;i++){if(a[i]==k){printf("Element %d found at position %d\\n",k,i+1);f=1;break;}}if(!f)printf("Element %d not found\\n",k);return 0;}`,
        binary_search: `#include <stdio.h>\nint bs(int a[],int n,int k){int l=0,h=n-1;while(l<=h){int m=l+(h-l)/2;if(a[m]==k)return m;else if(a[m]<k)l=m+1;else h=m-1;}return -1;}\nint main(){int n,k;if(scanf("%d",&n)!=1||n<=0)return 0;int a[n];for(int i=0;i<n;i++)scanf("%d",&a[i]);scanf("%d",&k);int idx=bs(a,n,k);if(idx!=-1)printf("Element %d found at index %d\\n",k,idx);else printf("Element %d not found\\n",k);return 0;}`,
        bubble_sort: `#include <stdio.h>\nvoid bs(int a[],int n){for(int i=0;i<n-1;i++){int s=0;for(int j=0;j<n-i-1;j++){if(a[j]>a[j+1]){int t=a[j];a[j]=a[j+1];a[j+1]=t;s=1;}}if(!s)break;}}\nint main(){int n;if(scanf("%d",&n)!=1||n<=0)return 0;int a[n];for(int i=0;i<n;i++)scanf("%d",&a[i]);bs(a,n);for(int i=0;i<n;i++)printf("%d ",a[i]);printf("\\n");return 0;}`,
        insertion_sort: `#include <stdio.h>\nvoid is(int a[],int n){for(int i=1;i<n;i++){int k=a[i],j=i-1;while(j>=0&&a[j]>k){a[j+1]=a[j];j--;}a[j+1]=k;}}\nint main(){int n;if(scanf("%d",&n)!=1||n<=0)return 0;int a[n];for(int i=0;i<n;i++)scanf("%d",&a[i]);is(a,n);for(int i=0;i<n;i++)printf("%d ",a[i]);printf("\\n");return 0;}`,
        array_insert_delete: `#include <stdio.h>\nint main(){int n,p,v,dp;if(scanf("%d",&n)!=1||n<=0)return 0;int a[100];for(int i=0;i<n;i++)scanf("%d",&a[i]);scanf("%d %d",&p,&v);if(p>=1&&p<=n+1){for(int i=n;i>=p;i--)a[i]=a[i-1];a[p-1]=v;n++;}for(int i=0;i<n;i++)printf("%d ",a[i]);printf("\\n");if(scanf("%d",&dp)==1){if(dp>=1&&dp<=n){for(int i=dp-1;i<n-1;i++)a[i]=a[i+1];n--;}for(int i=0;i<n;i++)printf("%d ",a[i]);printf("\\n");}return 0;}`,
        array_rotate: `#include <stdio.h>\nvoid rev(int a[],int s,int e){while(s<e){int t=a[s];a[s++]=a[e];a[e--]=t;}}\nint main(){int n,k;if(scanf("%d",&n)!=1||n<=0)return 0;int a[n];for(int i=0;i<n;i++)scanf("%d",&a[i]);scanf("%d",&k);k%=n;rev(a,0,k-1);rev(a,k,n-1);rev(a,0,n-1);for(int i=0;i<n;i++)printf("%d ",a[i]);printf("\\n");return 0;}`,
        ll_operations: `#include <stdio.h>\n#include <stdlib.h>\nstruct N{int d;struct N* next;};\nstruct N* ins(struct N* h,int d){struct N* n=(struct N*)malloc(sizeof(struct N));n->d=d;n->next=NULL;if(!h)return n;struct N* t=h;while(t->next)t=t->next;t->next=n;return h;}\nvoid disp(struct N* h){while(h){printf("%d -> ",h->d);h=h->next;}printf("NULL\\n");}\nint main(){int n,v;struct N* h=NULL;if(scanf("%d",&n)!=1||n<=0)return 0;for(int i=0;i<n;i++){scanf("%d",&v);h=ins(h,v);}disp(h);return 0;}`,
        ll_reverse: `#include <stdio.h>\n#include <stdlib.h>\nstruct N{int d;struct N* next;};\nstruct N* ins(struct N* h,int d){struct N* n=(struct N*)malloc(sizeof(struct N));n->d=d;n->next=NULL;if(!h)return n;struct N* t=h;while(t->next)t=t->next;t->next=n;return h;}\nstruct N* rev(struct N* h){struct N* p=NULL,*c=h,*nx=NULL;while(c){nx=c->next;c->next=p;p=c;c=nx;}return p;}\nvoid disp(struct N* h){while(h){printf("%d ",h->d);h=h->next;}printf("\\n");}\nint main(){int n,v;struct N* h=NULL;if(scanf("%d",&n)!=1||n<=0)return 0;for(int i=0;i<n;i++){scanf("%d",&v);h=ins(h,v);}h=rev(h);disp(h);return 0;}`
    };

    function inject(val) {
        let ok = false;
        document.querySelectorAll('.ace_editor').forEach(el => {
            if (el.env && el.env.editor) { el.env.editor.setValue(val, 1); ok = true; }
        });
        if (!ok && window.ace) {
            try { window.ace.edit(document.querySelector('.ace_editor')||'editor').setValue(val, 1); ok = true; } catch(e){}
        }
        if (!ok) {
            const ta = document.querySelector('textarea');
            if (ta) { ta.value = val; ta.dispatchEvent(new Event('input',{bubbles:true})); ta.dispatchEvent(new Event('change',{bubbles:true})); ok = true; }
        }
        return ok;
    }

    function findBtn(words) {
        const els = Array.from(document.querySelectorAll('button, a.btn, a, input[type="button"], input[type="submit"]'));
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

    function detectProb() {
        const t = (document.body.innerText || "").toLowerCase();
        if (t.includes("binary search")) return { topic: "searching", key: "binary_search", name: "Binary Search" };
        if (t.includes("linear search") || (t.includes("search") && t.includes("element"))) return { topic: "searching", key: "linear_search", name: "Linear Search" };
        if (t.includes("bubble sort")) return { topic: "sorting", key: "bubble_sort", name: "Bubble Sort" };
        if (t.includes("insertion sort") || t.includes("sort")) return { topic: "sorting", key: "insertion_sort", name: "Insertion Sort" };
        if (t.includes("rotate") || t.includes("rotation") || t.includes("shift")) return { topic: "arrays", key: "array_rotate", name: "Array Rotate" };
        if (t.includes("insert") || t.includes("delete") || t.includes("array")) return { topic: "arrays", key: "array_insert_delete", name: "Array Insert/Delete" };
        if (t.includes("reverse") && (t.includes("linked") || t.includes("node") || t.includes("list"))) return { topic: "linked_lists", key: "ll_reverse", name: "Linked List Reversal" };
        if (t.includes("linked") || t.includes("node") || t.includes("singly")) return { topic: "linked_lists", key: "ll_operations", name: "Linked List Traversal" };
        return { topic: "searching", key: "linear_search", name: "Linear Search" };
    }

    function updateDisplay() {
        const el = document.getElementById('alf-p');
        if (el) {
            el.innerHTML = `Search: <b>${COUNTS.searching}/${MAX_PER_TOPIC}</b> | Sort: <b>${COUNTS.sorting}/${MAX_PER_TOPIC}</b><br>Arrays: <b>${COUNTS.arrays}/${MAX_PER_TOPIC}</b> | Lists: <b>${COUNTS.linked_lists}/${MAX_PER_TOPIC}</b>`;
        }
    }

    let running = false;

    async function loop() {
        if (!running) return;
        const msg = document.getElementById('alf-msg');

        // Check if all 4 topics reached quota
        if (COUNTS.searching >= MAX_PER_TOPIC && COUNTS.sorting >= MAX_PER_TOPIC && COUNTS.arrays >= MAX_PER_TOPIC && COUNTS.linked_lists >= MAX_PER_TOPIC) {
            running = false;
            if (msg) msg.innerText = "🏆 4 Topics Completed! 1 Mark unlocked.";
            alert("[JARVIS X] All 4 topics completed! Test portal is unlocked.");
            return;
        }

        // 1. If on dashboard, click CONTINUE PRACTICE
        const continueBtn = findBtn(["continue practice", "continue", "practice"]);
        if (continueBtn && !document.querySelector('.ace_editor')) {
            if (msg) msg.innerText = "Entering Data Structure...";
            console.log("[ALFRED] Clicking 'CONTINUE PRACTICE'...");
            continueBtn.click();
            await new Promise(r => setTimeout(r, 2500));
            if (running) setTimeout(loop, 1500);
            return;
        }

        // 2. If on a question screen
        const hasEditor = document.querySelector('.ace_editor') || document.querySelector('.CodeMirror') || document.querySelector('#editor');
        if (hasEditor) {
            const p = detectProb();
            
            // Check if this topic is already done
            if (COUNTS[p.topic] >= MAX_PER_TOPIC) {
                if (msg) msg.innerText = `${p.topic.toUpperCase()} done (${MAX_PER_TOPIC}/${MAX_PER_TOPIC}). Back to wheel...`;
                const backBtn = findBtn(["home", "back", "topics", "dashboard"]);
                if (backBtn) { backBtn.click(); await new Promise(r => setTimeout(r, 2500)); }
                if (running) setTimeout(loop, 2000);
                return;
            }

            if (msg) msg.innerText = `[${p.topic}] Injecting ${p.name}...`;
            inject(CODE[p.key]);
            await new Promise(r => setTimeout(r, 1000));

            // Click Evaluate
            const evalBtn = findBtn(["evaluate", "submit", "compile & run", "run code"]);
            if (evalBtn) {
                if (msg) msg.innerText = "Evaluating test cases...";
                evalBtn.click();
            }

            await new Promise(r => setTimeout(r, 6000));

            COUNTS[p.topic]++;
            updateDisplay();

            if (COUNTS[p.topic] >= MAX_PER_TOPIC) {
                if (msg) msg.innerText = `✅ Finished ${p.topic}! Switching...`;
                const backBtn = findBtn(["home", "back", "topics", "dashboard"]);
                if (backBtn) { backBtn.click(); await new Promise(r => setTimeout(r, 2500)); }
            } else {
                const nextBtn = findBtn(["next", "next question", "next >>", ">"]);
                if (nextBtn) { nextBtn.click(); await new Promise(r => setTimeout(r, 2500)); }
            }
        } else {
            // On wheel screen, click next question / slice
            if (msg) msg.innerText = "Selecting question...";
            const q = findBtn(["question", "prob", "1", "2"]);
            if (q) { q.click(); await new Promise(r => setTimeout(r, 2500)); }
        }

        if (running) setTimeout(loop, 2000);
    }

    // Build Minimal HUD
    const old = document.getElementById('alf-hud');
    if (old) old.remove();

    const h = document.createElement('div');
    h.id = 'alf-hud';
    h.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999999;width:280px;background:#0d1117;border:2px solid #00ff88;border-radius:10px;padding:12px;color:#fff;font-family:monospace;font-size:12px;box-shadow:0 8px 24px rgba(0,0,0,0.8);';
    h.innerHTML = '<div style="display:flex;justify-content:space-between;font-weight:bold;color:#00ff88;margin-bottom:6px;"><span>🤖 ALFRED AUTOPILOT</span><span onclick="document.getElementById(\'alf-hud\').remove()" style="cursor:pointer;">✕</span></div><div id="alf-p" style="background:#161b22;padding:6px;border-radius:4px;margin-bottom:8px;line-height:1.5;">Search: 0/2 | Sort: 0/2<br>Arrays: 0/2 | Lists: 0/2</div><div style="display:flex;gap:6px;margin-bottom:6px;"><button id="alf-go" style="flex:2;background:#238636;color:#fff;border:none;padding:8px;border-radius:4px;font-weight:bold;cursor:pointer;">🚀 START</button><button id="alf-stop" style="flex:1;background:#da3633;color:#fff;border:none;padding:8px;border-radius:4px;font-weight:bold;cursor:pointer;">⏸ STOP</button></div><div id="alf-msg" style="color:#7ee787;font-size:11px;text-align:center;">Ready on Dashboard</div>';
    document.body.appendChild(h);

    document.getElementById('alf-go').onclick = () => {
        if (!running) { running = true; document.getElementById('alf-go').style.opacity = '0.5'; loop(); }
    };
    document.getElementById('alf-stop').onclick = () => {
        running = false; document.getElementById('alf-go').style.opacity = '1'; document.getElementById('alf-msg').innerText = "Paused";
    };

    updateDisplay();
    console.log("%c[ALFRED] ✅ Ready! Click [🚀 START] on the green box at bottom-right.", "color:#00ff88;font-weight:bold;");
})();
