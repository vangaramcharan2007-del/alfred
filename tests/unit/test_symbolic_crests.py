"""
Unit tests for Symbolic Crests (Spider E-V and Bat Alfred).
===========================================================
Verifies SVG validity, CSS definitions, and HUD endpoint responses for both crests.
"""

import unittest
from jarvisx.gui.symbolic_crests import SPIDER_CREST_SVG, BAT_CREST_SVG, CREST_CSS
from jarvisx.gui.spiderman_linux_hud import HTML_TEMPLATE


class TestSymbolicCrests(unittest.TestCase):

    def test_spider_crest_svg_validity(self):
        self.assertIn("<svg", SPIDER_CREST_SVG)
        self.assertIn("spider-crest-svg", SPIDER_CREST_SVG)
        self.assertIn("#00f0ff", SPIDER_CREST_SVG)
        self.assertIn("#ff003c", SPIDER_CREST_SVG)

    def test_bat_crest_svg_validity(self):
        self.assertIn("<svg", BAT_CREST_SVG)
        self.assertIn("bat-crest-svg", BAT_CREST_SVG)
        self.assertIn("#ffd700", BAT_CREST_SVG)

    def test_crest_css_classes(self):
        self.assertIn(".crest-btn", CREST_CSS)
        self.assertIn(".spider-btn", CREST_CSS)
        self.assertIn(".bat-btn", CREST_CSS)

    def test_html_template_contains_crests(self):
        self.assertIn("spider-btn", HTML_TEMPLATE)
        self.assertIn("bat-btn", HTML_TEMPLATE)
        self.assertIn("E-V CO-PILOT", HTML_TEMPLATE)
        self.assertIn("ALFRED BUTLER", HTML_TEMPLATE)


if __name__ == "__main__":
    unittest.main()
