// Alfred OS Chrome Companion — Background Service Worker

const ALFRED_API_URL = "http://127.0.0.1:8765";

// Setup Context Menus
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "alfred_explain_selection",
    title: "🧠 Ask Alfred to Explain Selection",
    contexts: ["selection"]
  });

  chrome.contextMenus.create({
    id: "alfred_save_second_brain",
    title: "📚 Save to Alfred Second Brain",
    contexts: ["page", "selection"]
  });

  chrome.contextMenus.create({
    id: "alfred_solve_in_vscode",
    title: "⚡ Solve with Alfred in VS Code",
    contexts: ["page", "selection"]
  });

  console.log("[Alfred Companion] Extension Installed & Context Menus Registered.");
});

// Handle Context Menu Actions
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const selectedText = info.selectionText || "";
  const pageUrl = tab?.url || "";
  const pageTitle = tab?.title || "";

  let actionType = "chat";
  let prompt = "";

  if (info.menuItemId === "alfred_explain_selection") {
    actionType = "explain";
    prompt = `Please explain the following selected code/concept in detail:\n\n${selectedText}\n\nContext Source: ${pageTitle} (${pageUrl})`;
  } else if (info.menuItemId === "alfred_save_second_brain") {
    actionType = "save_note";
    prompt = `Store this note in your Second Brain memory:\n\nTitle: ${pageTitle}\nURL: ${pageUrl}\nContent:\n${selectedText || "Full page reference"}`;
  } else if (info.menuItemId === "alfred_solve_in_vscode") {
    actionType = "solve_leetcode";
    prompt = `Solve this coding problem in Python and prepare the implementation file for VS Code:\n\nTitle: ${pageTitle}\nURL: ${pageUrl}\nDescription:\n${selectedText || "Active problem page"}`;
  }

  try {
    const response = await fetch(`${ALFRED_API_URL}/api/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: actionType,
        prompt: prompt,
        url: pageUrl,
        title: pageTitle,
        selection: selectedText
      })
    });

    const data = await response.json();
    console.log("[Alfred Companion] Response received:", data);

    // Send toast badge to active tab
    if (tab?.id) {
      chrome.tabs.sendMessage(tab.id, {
        type: "ALFRED_TOAST",
        title: "Alfred OS",
        message: data.spoken || data.response || "Action executed successfully by Alfred!"
      });
    }
  } catch (err) {
    console.warn("[Alfred Companion] Failed to connect to Alfred local bridge:", err);
    if (tab?.id) {
      chrome.tabs.sendMessage(tab.id, {
        type: "ALFRED_TOAST",
        title: "Alfred OS (Offline)",
        message: "Alfred Bridge is offline. Ensure Jarvis X / Alfred OS is running locally on port 8765."
      });
    }
  }
});

// Relay messages from Popup or Content Script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "CHECK_HEALTH") {
    fetch(`${ALFRED_API_URL}/api/status`)
      .then(res => res.json())
      .then(data => sendResponse({ status: "online", data }))
      .catch(err => sendResponse({ status: "offline", error: err.message }));
    return true; // async
  }

  if (request.type === "EXECUTE_ACTION") {
    fetch(`${ALFRED_API_URL}/api/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request.payload)
    })
      .then(res => res.json())
      .then(data => sendResponse({ status: "success", data }))
      .catch(err => sendResponse({ status: "error", error: err.message }));
    return true; // async
  }
});
