import unittest

from local_dictation.text import post_process_transcript


class PostProcessTranscriptTests(unittest.TestCase):
    def test_preserves_casing_except_first_letter(self):
        self.assertEqual(post_process_transcript("hello NASA"), "Hello NASA")

    def test_replaces_basic_punctuation_commands(self):
        self.assertEqual(
            post_process_transcript("hello comma world full stop", enable_spoken_punctuation=True),
            "Hello, world.",
        )

    def test_replaces_line_commands(self):
        self.assertEqual(
            post_process_transcript(
                "first new line second new paragraph third",
                enable_spoken_punctuation=True,
            ),
            "First\nsecond\n\nthird",
        )

    def test_empty_text_stays_empty(self):
        self.assertEqual(post_process_transcript("   "), "")

    def test_preserves_numbers_emails_and_abbreviations(self):
        self.assertEqual(
            post_process_transcript(
                "Order 3,250 units at 19.99 dollars, email john.doe@example.com by 5 p.m."
            ),
            "Order 3,250 units at 19.99 dollars, email john.doe@example.com by 5 p.m.",
        )

    def test_preserves_decimal_version_numbers(self):
        self.assertEqual(
            post_process_transcript("version large-v3 runs at 7.7 times realtime"),
            "Version large-v3 runs at 7.7 times realtime",
        )

    def test_spoken_punctuation_words_are_literal_by_default(self):
        self.assertEqual(
            post_process_transcript("we waited for a period then added a comma"),
            "We waited for a period then added a comma",
        )

    def test_spoken_punctuation_can_be_enabled(self):
        self.assertEqual(
            post_process_transcript(
                "hello comma world full stop",
                enable_spoken_punctuation=True,
            ),
            "Hello, world.",
        )

    def test_capitalization_can_be_disabled(self):
        self.assertEqual(
            post_process_transcript("hello NASA", capitalize=False),
            "hello NASA",
        )


if __name__ == "__main__":
    unittest.main()
