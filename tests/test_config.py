import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from local_dictation.config import (
    AppConfig,
    app_local_config_path,
    config_dir,
    effective_config_path,
    load_config,
    resolve_model_name,
    save_config,
)


class ConfigTests(unittest.TestCase):
    def test_defaults(self):
        config = AppConfig()
        self.assertEqual(config.model_name, "large-v3")
        self.assertEqual(config.device, "cuda")
        self.assertEqual(config.compute_type, "float16")
        self.assertEqual(config.language, "en")
        self.assertTrue(config.unload_model_when_idle)
        self.assertEqual(config.unload_after_seconds, 300)
        self.assertFalse(config.enable_spoken_punctuation)
        self.assertTrue(config.capitalize_transcript)
        self.assertFalse(config.type_text_instead_of_paste)

    def test_load_ignores_unknown_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps({"model_name": "tiny", "ignored": True}), encoding="utf-8")
            config = load_config(path)
            self.assertEqual(config.model_name, "tiny")
            self.assertFalse(hasattr(config, "ignored"))

    def test_save_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            original = AppConfig(language="en", beam_size=1)
            save_config(original, path)
            loaded = load_config(path)
            self.assertEqual(loaded.language, "en")
            self.assertEqual(loaded.beam_size, 1)

    def test_load_accepts_utf8_bom(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps({"model_name": "tiny"}), encoding="utf-8-sig")
            loaded = load_config(path)
            self.assertEqual(loaded.model_name, "tiny")

    def test_config_dir_uses_appdata_on_windows(self):
        with patch.dict("os.environ", {"APPDATA": r"C:\Users\me\AppData\Roaming"}, clear=True):
            self.assertEqual(config_dir(), Path(r"C:\Users\me\AppData\Roaming") / "LocalWhisperDictation")

    def test_config_dir_uses_xdg_config_home_without_appdata(self):
        with patch.dict("os.environ", {"XDG_CONFIG_HOME": "/tmp/config"}, clear=True):
            self.assertEqual(config_dir(), Path("/tmp/config") / "LocalWhisperDictation")

    def test_effective_config_path_uses_env_override(self):
        with patch.dict("os.environ", {"LOCAL_DICTATION_CONFIG": "/tmp/custom-settings.json"}, clear=True):
            self.assertEqual(effective_config_path(), Path("/tmp/custom-settings.json"))

    def test_app_local_config_path_uses_cwd_when_not_frozen(self):
        self.assertEqual(app_local_config_path(), Path.cwd() / "settings.json")

    def test_load_config_can_read_app_local_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = Path(tmp) / "settings.json"
            settings.write_text(json.dumps({"device": "cpu", "compute_type": "int8"}), encoding="utf-8")
            with patch.dict("os.environ", {}, clear=True), patch("pathlib.Path.home", return_value=Path(tmp) / "home"):
                original_cwd = Path.cwd()
                try:
                    import os

                    os.chdir(tmp)
                    config = load_config()
                finally:
                    os.chdir(original_cwd)

        self.assertEqual(config.device, "cpu")
        self.assertEqual(config.compute_type, "int8")

    def test_packaging_profiles_are_valid_configs(self):
        profiles = [
            Path("packaging/profiles/gpu-large-v3.json"),
            Path("packaging/profiles/cpu-small-en.json"),
        ]

        loaded = [load_config(path) for path in profiles]

        self.assertEqual(loaded[0].device, "cuda")
        self.assertEqual(loaded[0].model_name, "large-v3")
        self.assertEqual(loaded[1].device, "cpu")
        self.assertEqual(loaded[1].compute_type, "int8")
        self.assertEqual(loaded[1].model_name, "small.en")

    def test_resolve_model_name_uses_local_large_v3_when_present(self):
        expected = Path.cwd() / "models" / "faster-whisper-large-v3"
        if not expected.exists():
            self.skipTest("local large-v3 model is not present")

        self.assertEqual(resolve_model_name("large-v3"), str(expected))


if __name__ == "__main__":
    unittest.main()
