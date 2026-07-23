import pytest
import os
from jarvisx.core.context import DeviceContext

def test_device_context_windows():
    ctx = DeviceContext(platform_name="Windows")
    assert ctx.is_windows is True
    assert ctx.is_linux is False
    assert ctx.is_macos is False
    assert ctx.active_device == "desktop"
    assert "desktop_automation" in ctx.available_capabilities

def test_device_context_linux():
    ctx = DeviceContext(platform_name="Linux")
    assert ctx.is_windows is False
    assert ctx.is_linux is True
    assert ctx.active_device == "desktop"

def test_device_context_android(monkeypatch):
    monkeypatch.setenv("ANDROID_ROOT", "/system")
    ctx = DeviceContext(platform_name="Linux")
    assert ctx.is_android is True
    assert ctx.active_device == "mobile"
    assert "mobile_automation" in ctx.available_capabilities
