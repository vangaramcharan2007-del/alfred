import asyncio
import os
from jarvisx.core.tools.browser import (
    BrowserManager, PageController, ElementLocator, FormHandler,
    Extractor, SessionManager, ScreenshotManager, Observer
)

async def validate():
    print("=== JARVIS X BROWSER LAYER VALIDATION ===")
    
    # 1. Launch Chromium
    print("\n1. Launching Chromium")
    manager = BrowserManager.get_instance()
    await manager.launch(headless=True)
    
    # 2. Open example.com
    print("\n2. Opening example.com")
    await PageController.navigate("https://example.com")
    await Observer.wait_for_page_ready()
    
    # 3. Extract page title
    title = await Extractor.extract_title()
    print(f"\n3. Page title: {title}")
    
    # 4. Open Wikipedia
    print("\n4. Opening Wikipedia")
    await PageController.navigate("https://en.wikipedia.org/wiki/Main_Page")
    await Observer.wait_for_page_ready()
    
    # 5. Search for "Artificial Intelligence"
    print("\n5. Searching for 'Artificial Intelligence'")
    await FormHandler.type("css", "input[name='search']", "Artificial Intelligence")
    await FormHandler.click("css", "button:has-text('Search')")
    await Observer.wait_for_page_ready()
    
    # 6. Extract first paragraph
    print("\n6. Extracting text")
    text = await Extractor.extract_text()
    print(f"First paragraph: {text[:100]}...")
    
    # 7. Open second tab
    print("\n7. Opening second tab")
    await PageController.new_tab(new_page_id="tab2")
    await PageController.navigate("https://example.com", page_id="tab2")
    
    # 8. Capture screenshot
    print("\n8. Capturing screenshot")
    await ScreenshotManager.capture_viewport("var/validation_screenshot.png", page_id="tab2")
    print(f"Screenshot exists: {os.path.exists('var/validation_screenshot.png')}")
    
    # 9. Save session state
    print("\n9. Saving session state")
    await SessionManager.save_state()
    
    # 10. Close browser
    print("\n10. Closing browser")
    await manager.shutdown()
    
    # 11. Restore session
    print("\n11. Restoring session")
    manager = BrowserManager.get_instance()
    await SessionManager.restore_state()
    
    # 12. Verify session restoration
    print("\n12. Verifying session")
    context = await manager.create_context("default")
    pages = context.pages
    print(f"Context loaded. Ready to continue operations.")
    
    await manager.shutdown()

if __name__ == "__main__":
    asyncio.run(validate())
