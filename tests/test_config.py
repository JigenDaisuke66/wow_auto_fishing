import json
import unittest
from unittest.mock import patch

from fishing_assistant.config import AppConfig, load_config, save_config
from fishing_assistant.texts import EN_US, ZH_CN, text


class ConfigTests(unittest.TestCase):
    def test_old_config_is_compatible(self):
        old_data = json.dumps({"game_window_title": "魔兽世界", "difference_threshold": 35})
        with patch("pathlib.Path.exists", return_value=True), patch(
            "pathlib.Path.read_text", return_value=old_data
        ):
            config = load_config()
        self.assertEqual(config.game_window_title, "魔兽世界")
        self.assertEqual(config.difference_threshold, 35)
        self.assertEqual(config.confirmation_frames, 2)

    def test_afk_range_is_normalized(self):
        config = AppConfig(afk_time_min=20, afk_time_max=10)
        config.normalize()
        self.assertEqual(config.afk_time_max, 20)

    def test_unicode_paths_round_trip_serialization(self):
        config = AppConfig(image_paths=[r"D:\截图\浮漂.png"])
        with patch("pathlib.Path.write_text") as write_text:
            save_config(config)
        serialized = write_text.call_args.args[0]
        self.assertEqual(json.loads(serialized)["image_paths"], [r"D:\截图\浮漂.png"])
        self.assertIn("浮漂.png", serialized)

    def test_old_config_defaults_to_chinese(self):
        with patch("pathlib.Path.exists", return_value=True), patch(
            "pathlib.Path.read_text", return_value="{}"
        ):
            self.assertEqual(load_config().language, "zh_CN")

    def test_translation_keys_match(self):
        self.assertEqual(set(ZH_CN), set(EN_US))
        self.assertEqual(text("start", "en_US"), "Start")


if __name__ == "__main__":
    unittest.main()
