#!/usr/bin/env python3
"""
Test marks lesson functionality
"""

import os
import sys
import unittest

# Import the Vimtut class from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from vimtut import Vimtut


class TestMarksLesson(unittest.TestCase):
    """Test that marks lesson properly creates a long file and validates mark usage."""

    def setUp(self):
        """Set up test environment."""
        self.vimtut = Vimtut()
        self.lesson = self.vimtut.get_lesson_by_id("marks")
        self.assertIsNotNone(self.lesson, "Lesson 'marks' should exist")

    def tearDown(self):
        """Clean up after tests."""
        self.vimtut.cleanup_lesson(self.lesson)

    def test_setup_creates_file_with_markers(self):
        """Test that setup creates a file with DELETE_THIS markers."""
        self.vimtut.setup_lesson(self.lesson)

        task_file = self.vimtut.workspace_dir / "current_task.txt"
        self.assertTrue(task_file.exists(), "current_task.txt should be created")

        with open(task_file, 'r') as f:
            content = f.read()

        delete_count = content.count('DELETE_THIS')
        self.assertEqual(delete_count, 3, f"Should have 3 DELETE_THIS markers, found {delete_count}")

    def test_validation_fails_before_edit(self):
        """Test that validation fails before DELETE_THIS words are removed."""
        self.vimtut.setup_lesson(self.lesson)

        success, message = self.vimtut.validate_lesson(self.lesson)
        self.assertFalse(success, "Validation should fail before removing DELETE_THIS")

    def test_validation_passes_after_edit(self):
        """Test that validation passes after DELETE_THIS words are removed."""
        self.vimtut.setup_lesson(self.lesson)

        task_file = self.vimtut.workspace_dir / "current_task.txt"
        with open(task_file, 'r') as f:
            content = f.read()

        # Remove all DELETE_THIS occurrences
        content_cleaned = content.replace('DELETE_THIS ', '')

        with open(task_file, 'w') as f:
            f.write(content_cleaned)

        success, message = self.vimtut.validate_lesson(self.lesson)
        self.assertTrue(success, f"Validation should pass after removing DELETE_THIS: {message}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
