"""
Unit Test Suite for Minimalist Logo Overlay Widget.
===================================================
"""

import unittest
from unittest.mock import patch, MagicMock

from jarvisx.gui.ev_minimalist_logo_overlay import EVMinimalistLogoOverlay


class TestEVMinimalistLogoOverlay(unittest.TestCase):

    @patch("tkinter.Tk")
    def test_overlay_initialization(self, mock_tk_class):
        mock_root = MagicMock()
        mock_tk_class.return_value = mock_root
        mock_root.winfo_screenwidth.return_value = 1920

        overlay = EVMinimalistLogoOverlay()
        mock_root.overrideredirect.assert_called_once_with(True)
        mock_root.attributes.assert_any_call("-topmost", True)
        mock_root.attributes.assert_any_call("-alpha", 0.92)

    @patch("jarvisx.automation.ev_master_automation_engine.EVMasterAutomationEngine.get_instance")
    def test_button_callbacks(self, mock_engine):
        with patch("tkinter.Tk") as mock_tk:
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            mock_root.winfo_screenwidth.return_value = 1920

            overlay = EVMinimalistLogoOverlay()
            
            overlay._on_spider_click()
            overlay._on_cool_click()
            overlay._on_bat_click()


if __name__ == "__main__":
    unittest.main()
