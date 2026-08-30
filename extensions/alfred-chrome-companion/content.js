// Alfred OS Chrome Companion — Content Script

console.log("[Alfred Companion] Content script injected on", window.location.href);

// Listen for messages from background/popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "GET_PAGE_CONTEXT") {
    const context = extractPageContext();
    sendResponse(context);
    return true;
  }

  if (request.type === "ALFRED_TOAST") {
    showAlfredToast(request.title, request.message);
    sendResponse({ status: "displayed" });
    return true;
  }
});

// Intelligent Page Context Extractor
function extractPageContext() {
  const url = window.location.href;
  const title = document.title;
  const selection = window.getSelection()?.toString() || "";

  // Specialized: LeetCode Problem Extraction
  if (url.includes("leetcode.com/problems/")) {
    const problemTitle = document.querySelector("div[class*='text-title-large']")?.textContent?.trim() || title;
    const difficulty = document.querySelector("div[class*='text-difficulty']")?.textContent?.trim() || "Medium";
    const contentDiv = document.querySelector("div[data-track-load='description_content']") || document.querySelector("div[class*='elfjS']");
    const description = contentDiv?.innerText?.slice(0, 3000) || "";

    return {
      type: "leetcode",
      url,
      title: problemTitle,
      difficulty,
      selection,
      description: description,
      rawText: `${problemTitle} (${difficulty})\n\n${description}`
    };
  }

  // Specialized: YouTube Video Extraction
  if (url.includes("youtube.com/watch")) {
    const videoTitle = document.querySelector("h1.ytd-watch-metadata yt-formatted-string")?.textContent?.trim() || title;
    const channel = document.querySelector("#channel-name #text a")?.textContent?.trim() || "";
    const videoElem = document.querySelector("video");
    const currentTime = videoElem ? Math.floor(videoElem.currentTime) : 0;
    const minutes = Math.floor(currentTime / 60);
    const seconds = currentTime % 60;
    const timeFormatted = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

    return {
      type: "youtube",
      url,
      title: videoTitle,
      channel,
      currentTime: timeFormatted,
      selection,
      rawText: `YouTube Video: ${videoTitle} by ${channel} at timestamp [${timeFormatted}]`
    };
  }

  // General Web Page Context
  const bodyClone = document.body.cloneNode(true);
  // Strip script, style, svg, nav
  bodyClone.querySelectorAll("script, style, svg, nav, footer, noscript").forEach(el => el.remove());
  const bodyText = (bodyClone.innerText || "").replace(/\s+/g, " ").trim().slice(0, 3000);

  return {
    type: "general",
    url,
    title,
    selection,
    rawText: bodyText
  };
}

// In-Page Toast Notification Badge
function showAlfredToast(title, message) {
  let toast = document.getElementById("alfred-hud-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "alfred-hud-toast";
    toast.className = "alfred-hud-toast-container";
    document.body.appendChild(toast);
  }

  const shortMsg = message.length > 250 ? message.slice(0, 250) + "..." : message;

  toast.innerHTML = `
    <div class="alfred-toast-header">
      <div class="alfred-toast-indicator"></div>
      <span class="alfred-toast-title">⚡ ${title || "Alfred OS"}</span>
      <span class="alfred-toast-close">&times;</span>
    </div>
    <div class="alfred-toast-body">${escapeHtml(shortMsg)}</div>
  `;

  toast.classList.add("alfred-toast-visible");

  const closeBtn = toast.querySelector(".alfred-toast-close");
  closeBtn.onclick = () => toast.classList.remove("alfred-toast-visible");

  setTimeout(() => {
    toast.classList.remove("alfred-toast-visible");
  }, 6000);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
