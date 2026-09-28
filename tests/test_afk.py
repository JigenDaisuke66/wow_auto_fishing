"""Regression coverage for issue #3; all keyboard input is mocked."""

import unittest
from unittest.mock import patch

from fishing_assistant.config import AppConfig
from fishing_assistant.texts import text
from fishing_assistant.worker import FishingWorker


class AfkTests(unittest.TestCase):
    def test_due_afk_logs_and_reschedules_in_both_languages(self):
        for language in ("zh_CN", "en_US"):
            with self.subTest(language=language):
                worker = FishingWorker(AppConfig(language=language, afk_key="space"))
                messages = []
                worker.log_signal.connect(messages.append)
                with patch("fishing_assistant.worker.pyautogui.press") as press, patch(
                    "fishing_assistant.worker.time.monotonic", return_value=1000
                ), patch("fishing_assistant.worker.random.uniform", return_value=600):
                    next_at = worker._maybe_afk(1000)
                    self.assertEqual(next_at, 1600)
                    self.assertEqual(worker._maybe_afk(next_at), 1600)
                    press.assert_called_once_with("space")
                self.assertEqual(messages, [text("afk_pressed", language, key="space")])
                self.assertIn("space", messages[0])


if __name__ == "__main__":
    unittest.main()
