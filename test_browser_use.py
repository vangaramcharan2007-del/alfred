import asyncio
from src.jarvisx.browser.browser_use_engine import BrowserUseEngine

async def test_browser():
    engine = BrowserUseEngine.get_instance()
    engine.start()
    
    # We will await the inner async function directly for testing
    print("Starting Browser-Use test...")
    await engine._async_execute("Go to github.com and search for the browser-use repository.")

if __name__ == "__main__":
    asyncio.run(test_browser())
