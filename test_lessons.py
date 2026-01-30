#!/usr/bin/env python3
"""
Test individual lessons to verify their validation logic
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# Import the VimDojo class
sys.path.insert(0, os.path.dirname(__file__))
from dojo_app import VimDojo


class TestLessonContent(unittest.TestCase):
    """Test specific lessons have correct expected content."""

    def setUp(self):
        """Load all lessons."""
        self.dojo = VimDojo()

    def test_lesson_02_navigation_delete_m(self):
        """Test lesson 2 - deleting 'M' produces correct output."""
        lesson = self.dojo.get_lesson_by_id("02_navigation_hjkl")
        self.assertIsNotNone(lesson)

        # Simulate the task: delete 'M' from the setup file
        original = lesson['setup_file']
        expected = lesson['target_content']

        # The setup has "K L M N O" on line 3
        # After deleting M, it should be "K L  N O" (two spaces)
        self.assertIn("K L M N O", original, "Setup should contain 'K L M N O'")
        self.assertIn("K L  N O", expected, "Target should contain 'K L  N O' (two spaces)")
        self.assertNotIn("K L   N O", expected, "Target should NOT have three spaces")

        # Verify the deletion manually
        result = original.replace("K L M N O", "K L  N O")
        self.assertEqual(result, expected, "Deleting M should produce expected target")

    def test_lesson_03_insert_brown(self):
        """Test lesson 3 - inserting 'brown' is correct."""
        lesson = self.dojo.get_lesson_by_id("03_insert_mode")
        self.assertIsNotNone(lesson)

        original = lesson['setup_file']
        expected = lesson['target_content']

        self.assertEqual(original, "The quick fox jumps over the lazy dog.")
        self.assertEqual(expected, "The quick brown fox jumps over the lazy dog.")

    def test_lesson_06_delete_extra_letters(self):
        """Test lesson 6 - deleting extra letters."""
        lesson = self.dojo.get_lesson_by_id("06_delete_char")
        self.assertIsNotNone(lesson)

        original = lesson['setup_file']
        expected = lesson['target_content']

        self.assertEqual(original, "Helllllo Worrrlld")
        self.assertEqual(expected, "Hello World")

    def test_lesson_07_delete_lines(self):
        """Test lesson 7 - deleting specific lines."""
        lesson = self.dojo.get_lesson_by_id("07_delete_line")
        self.assertIsNotNone(lesson)

        original = lesson['setup_file']
        expected = lesson['target_content']

        # Should have 5 lines in setup, 3 in target
        self.assertEqual(len(original.split('\n')), 5)
        self.assertEqual(len(expected.split('\n')), 3)

        # Should keep Apple, Banana, Cherry
        self.assertIn("Apple", expected)
        self.assertIn("Banana", expected)
        self.assertIn("Cherry", expected)

        # Should remove DELETE ME and REMOVE THIS
        self.assertNotIn("DELETE ME", expected)
        self.assertNotIn("REMOVE THIS", expected)

    def test_all_lessons_have_required_fields(self):
        """Ensure all lessons have required fields."""
        required_fields = ['id', 'title', 'instruction_text', 'setup_file',
                          'validation_type', 'target_content']

        for lesson in self.dojo.lessons:
            for field in required_fields:
                self.assertIn(field, lesson,
                             f"Lesson {lesson.get('id', 'unknown')} missing field: {field}")

    def test_validation_types_are_valid(self):
        """Ensure all lessons use valid validation types."""
        valid_types = ['file_saved', 'exact_match', 'contains', 'exact_match_file']

        for lesson in self.dojo.lessons:
            validation_type = lesson.get('validation_type')
            self.assertIn(validation_type, valid_types,
                         f"Lesson {lesson['id']} has invalid validation_type: {validation_type}")


def run_tests():
    """Run all lesson content tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLessonContent)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Testing lesson content and structure...\n")
    success = run_tests()

    if success:
        print("\n✅ All lesson tests passed!")
    else:
        print("\n❌ Some lesson tests failed!")

    sys.exit(0 if success else 1)
