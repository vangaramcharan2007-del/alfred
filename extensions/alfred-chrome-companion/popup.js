// Alfred OS Chrome Companion — Popup Script

const ALFRED_API_URL = "http://127.0.0.1:8765";

let activeContext = {
  type: "general",
  title: "",
  url: "",
  rawText: ""
};

document.addEventListener("DOMContentLoaded", async () => {
  const statusBadge = document.getElementById("connection-status");
  const statusLabel = document.getElementById("status-label");
  const pageTitleElem = document.getElementById("page-title");
  const contextTagElem = document.getElementById("context-tag");
  const responseContainer = document.getElementById("response-container");
  const responseText = document.getElementById("response-text");
  const promptInput = document.getElementById("user-prompt-input");
  const sendBtn = document.getElementById("btn-send-prompt");
  const copyBtn = document.getElementById("btn-copy-response");

  // 1. Check Alfred Engine Health
  try {
    const res = await fetch(`${ALFRED_API_URL}/api/status`, { method: "GET" });
    if (res.ok) {
      const data = await res.json();
      statusBadge.className = "alfred-status-badge status-online";
      statusLabel.textContent = `ONLINE (${data.persona || "ALFRED"})`;
      document.getElementById("hardware-vitals").textContent = `${data.llm_provider || "Groq LPU"} | Memory Active`;
    } else {
      setOffline();
    }
  } catch {
    setOffline();
  }

  function setOffline() {
    statusBadge.className = "alfred-status-badge status-offline";
    statusLabel.textContent = "BRIDGE OFFLINE";
    document.getElementById("hardware-vitals").textContent = "Start Jarvis X to connect local engine";
  }

  // 2. Query Active Chrome Tab
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
      pageTitleElem.textContent = tab.title || tab.url || "New Tab";
      
      // Request context from content script
      chrome.tabs.sendMessage(tab.id, { type: "GET_PAGE_CONTEXT" }, (context) => {
        if (context) {
          activeContext = context;
          pageTitleElem.textContent = context.title || tab.title;
          
          if (context.type === "leetcode") {
            contextTagElem.textContent = `LeetCode (${context.difficulty || "Problem"})`;
            contextTagElem.style.background = "rgba(245, 158, 11, 0.2)";
            contextTagElem.style.color = "#f59e0b";
            contextTagElem.style.borderColor = "rgba(245, 158, 11, 0.4)";
          } else if (context.type === "youtube") {
            contextTagElem.textContent = `YouTube [${context.currentTime || "0:00"}]`;
            contextTagElem.style.background = "rgba(244, 63, 94, 0.2)";
            contextTagElem.style.color = "#f43f5e";
            contextTagElem.style.borderColor = "rgba(244, 63, 94, 0.4)";
          } else {
            contextTagElem.textContent = "Web Page";
          }
        }
      });
    }
  } catch (err) {
    pageTitleElem.textContent = "Active Tab";
  }

  // 3. Quick Action Buttons
  document.getElementById("btn-solve-leetcode").addEventListener("click", () => {
    executeAction("solve_leetcode", `Solve the problem '${activeContext.title}' in Python. Implement clean solution and test cases:\n\n${activeContext.rawText}`);
  });

  document.getElementById("btn-summarize-page").addEventListener("click", () => {
    executeAction("summarize", `Summarize the core takeaways and key technical points from this page:\n\nTitle: ${activeContext.title}\nURL: ${activeContext.url}\n\nContent:\n${activeContext.rawText}`);
  });

  document.getElementById("btn-save-brain").addEventListener("click", () => {
    executeAction("save_note", `Save this resource and structured key points to Alfred Second Brain:\n\nTitle: ${activeContext.title}\nURL: ${activeContext.url}\n\nNotes:\n${activeContext.rawText}`);
  });

  document.getElementById("btn-remind-me").addEventListener("click", () => {
    const defaultTime = "in 30 minutes";
    executeAction("reminder", `Remind me ${defaultTime} to check back on: ${activeContext.title}`);
  });

  // 4. Custom Prompt Send
  sendBtn.addEventListener("click", () => {
    const val = promptInput.value.trim();
    if (val) {
      executeAction("chat", `${val}\n\n[Active Page Context: ${activeContext.title} (${activeContext.url})]\n${activeContext.selection ? "Selected Text: " + activeContext.selection : ""}`);
      promptInput.value = "";
    }
  });

  promptInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      sendBtn.click();
    }
  });

  // 5. Copy Response
  copyBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(responseText.textContent);
    copyBtn.textContent = "Copied!";
    setTimeout(() => { copyBtn.textContent = "Copy"; }, 2000);
  });

  // 6. Action Execution Handler
  async function executeAction(actionType, promptText) {
    responseContainer.classList.remove("hidden");
    responseText.textContent = "⚡ Alfred is processing via Groq LPU reflex brain...";

    try {
      const res = await fetch(`${ALFRED_API_URL}/api/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: actionType,
          prompt: promptText,
          url: activeContext.url,
          title: activeContext.title
        })
      });

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const data = await res.json();
      const output = data.response || data.spoken || JSON.stringify(data, null, 2);
      responseText.textContent = output;
    } catch (err) {
      responseText.textContent = `[Connection Notice]: Could not reach Alfred Bridge server on port 8765.\n\nMake sure Alfred OS / Jarvis X is active. Error: ${err.message}`;
    }
  }
});
