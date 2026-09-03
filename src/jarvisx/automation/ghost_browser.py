"""
Ghost Browser Engine — The Invisible Automation Shield.
Uses Playwright to spawn a headless background browser.
Reads chat DOMs (Discord/WhatsApp Web) and injects LLM replies autonomously
without needing official API keys or hijacking the physical mouse.

Phase 14: MAX AUTOMATION.
"""
import asyncio
import logging
import threading
from typing import Optional

from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class GhostBrowserEngine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self.browser = None
        self.context = None
        self.page = None
        
        # We store the last message so we don't reply twice
        self.last_seen_message = ""

    def _push_to_ui(self, event_type: str, data: dict):
        """Broadcast events to E.V. UI."""
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    async def _init_browser(self):
        """Initialize the headless browser."""
        logger.info("[GhostBrowser] Initializing headless Playwright engine...")
        self.playwright = await async_playwright().start()
        
        # Headless=True for max background automation. Set to False if login is needed.
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        logger.info("[GhostBrowser] Ghost Session Active.")
        self._push_to_ui("module_boot", {"name": "GhostBrowserEngine", "status": "ONLINE (INVISIBLE)"})

    async def _mock_navigation(self):
        """For testing purposes, we navigate to a safe page and inject a fake chat interface."""
        await self.page.goto("data:text/html,<html><body><div id='chat'><div class='msg'>Hey, can you fix my printer?</div></div><input id='replyBox'></body></html>")
        await asyncio.sleep(2)

    async def _read_latest_message(self) -> str:
        """Reads the DOM to find the latest incoming message."""
        try:
            # Example CSS selector for our mock chat. 
            # Real world: 'div[role="message"]' for Discord, '.copyable-text' for WhatsApp.
            msg_element = await self.page.query_selector(".msg:last-child")
            if msg_element:
                text = await msg_element.inner_text()
                return text.strip()
        except Exception as e:
            logger.debug(f"[GhostBrowser] DOM Read Error: {e}")
        return ""

    async def _type_and_send_reply(self, reply_text: str):
        """Types the response into the chat box and sends it."""
        try:
            logger.info(f"[GhostBrowser] Injecting reply into DOM: '{reply_text}'")
            self._push_to_ui("ghost_event", {"action": "Typing Reply...", "text": reply_text})
            
            # Real world: 'div[role="textbox"]' for Discord
            input_box = await self.page.query_selector("#replyBox")
            if input_box:
                await input_box.fill(reply_text)
                await asyncio.sleep(0.5) # humanize typing
                await input_box.press("Enter")
                logger.info("[GhostBrowser] Reply sent successfully.")
                self._push_to_ui("ghost_event", {"action": "Reply Sent", "text": reply_text})
        except Exception as e:
            logger.error(f"[GhostBrowser] Failed to inject reply: {e}")

    async def _background_loop(self):
        await self._init_browser()
        await self._mock_navigation()

        logger.info("[GhostBrowser] Monitoring DOM for incoming messages...")
        
        while self._running:
            try:
                latest_msg = await self._read_latest_message()
                
                # If we see a new message that we haven't replied to
                if latest_msg and latest_msg != self.last_seen_message:
                    logger.info(f"[GhostBrowser] Intercepted new message: '{latest_msg}'")
                    self._push_to_ui("ghost_event", {"action": "Intercepted Message", "text": latest_msg})
                    self.last_seen_message = latest_msg
                    
                    # Pass to E.X.E.C. for LLM triage
                    from jarvisx.automation.executive_function import ExecutiveFunctionProtocol
                    exec_protocol = ExecutiveFunctionProtocol.get_instance()
                    
                    # Offload LLM generation to avoid blocking the browser loop
                    reply = await asyncio.to_thread(exec_protocol.auto_triage_inbox, latest_msg)
                    
                    if reply:
                        await self._type_and_send_reply(reply)

                await asyncio.sleep(3)  # Poll DOM every 3 seconds
                
            except Exception as e:
                logger.error(f"[GhostBrowser] Loop error: {e}")
                await asyncio.sleep(5)
                
        await self.browser.close()
        await self.playwright.stop()

    def _start_async_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._background_loop())

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._start_async_loop, daemon=True, name="GhostBrowser")
        self._thread.start()

    def stop(self):
        self._running = False
