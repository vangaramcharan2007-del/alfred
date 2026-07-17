import pytest
import os
import asyncio
from jarvisx.core.tools.browser import (
    BrowserManager, PageController, ElementLocator, FormHandler,
    Extractor, SessionManager, ScreenshotManager, BrowserPermissionManager, BrowserTrustLevel
)

import pytest_asyncio

@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    # Setup
    BrowserPermissionManager.set_level(BrowserTrustLevel.ADMIN_ACTIONS)
    yield
    # Teardown
    await BrowserManager.get_instance().shutdown()


@pytest.mark.asyncio
async def test_browser_startup_and_navigation():
    success = await PageController.navigate("https://example.com")
    assert success == True
    title = await Extractor.extract_title()
    assert "Example Domain" in title

@pytest.mark.asyncio
async def test_extraction():
    await PageController.navigate("https://example.com")
    links = await Extractor.extract_links()
    assert len(links) > 0
    assert "iana.org/domains/example" in links[0]['href']

@pytest.mark.asyncio
async def test_form_interaction():
    await PageController.navigate("https://en.wikipedia.org/wiki/Main_Page")
    await FormHandler.type("css", "input[name='search']", "Test")
    locator = await ElementLocator.get_locator("css", "input[name='search']")
    val = await locator.first.input_value()
    assert val == "Test"

@pytest.mark.asyncio
async def test_screenshots():
    await PageController.navigate("https://example.com")
    path = await ScreenshotManager.capture_viewport("var/test_shot.png")
    assert os.path.exists(path)
    os.remove(path)

@pytest.mark.asyncio
async def test_tab_management():
    page1 = await BrowserManager.get_instance().get_page(page_id="main")
    page2 = await PageController.new_tab(new_page_id="tab2")
    assert page1 != page2
    await PageController.close_tab(page_id="tab2")

@pytest.mark.asyncio
async def test_permissions():
    BrowserPermissionManager.set_level(BrowserTrustLevel.READ_ONLY)
    with pytest.raises(PermissionError):
        await FormHandler.click("css", "button")
