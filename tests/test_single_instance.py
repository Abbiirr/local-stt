import unittest

from local_dictation.single_instance import should_lock_for_argv


class SingleInstanceTests(unittest.TestCase):
    def test_default_command_uses_instance_lock(self):
        self.assertTrue(should_lock_for_argv(["LocalWhisperDictation.exe"]))

    def test_run_command_uses_instance_lock(self):
        self.assertTrue(should_lock_for_argv(["local-dictation", "run"]))

    def test_cli_commands_do_not_use_instance_lock(self):
        self.assertFalse(should_lock_for_argv(["local-dictation", "print-config"]))


if __name__ == "__main__":
    unittest.main()
