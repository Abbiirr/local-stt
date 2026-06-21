import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from local_dictation.overlay import WaveOverlay


class WaveOverlayFocusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_overlay_does_not_accept_focus(self):
        overlay = WaveOverlay()
        self.assertTrue(overlay.windowFlags() & Qt.WindowType.WindowDoesNotAcceptFocus)

    def test_overlay_shows_without_activating(self):
        overlay = WaveOverlay()
        self.assertTrue(overlay.testAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating))


if __name__ == "__main__":
    unittest.main()
