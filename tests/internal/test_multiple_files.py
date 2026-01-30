#!/usr/bin/env python3
"""
Test multiple files lesson functionality
"""

import os
import sys
import unittest

# Import the Vimtut class from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from vimtut import Vimtut


class TestMultipleFilesLesson(unittest.TestCase):
    """Test that multiple_files lesson properly creates and validates second file."""

    def setUp(self):
        """Set up test environment."""
        self.vimtut = Vimtut()
        self.lesson = self.vimtut.get_lesson_by_id("multiple_files")
        self.assertIsNotNone(self.lesson, "Lesson 'multiple_files' should exist")

    def tearDown(self):
        """Clean up after tests."""
        self.vimtut.cleanup_lesson(self.lesson)

    def test_setup_creates_both_files(self):
        """Test that setup creates both current_task.txt and task2.txt."""
        self.vimtut.setup_lesson(self.lesson)

        task1 = self.vimtut.workspace_dir / "current_task.txt"
        task2 = self.vimtut.workspace_dir / "task2.txt"

        self.assertTrue(task1.exists(), "current_task.txt should be created")
        self.assertTrue(task2.exists(), "task2.txt should be created")

    def test_validation_fails_before_edit(self):
        """Test that validation fails before task2.txt is edited."""
        self.vimtut.setup_lesson(self.lesson)

        success, message = self.vimtut.validate_lesson(self.lesson)
        self.assertFalse(success, "Validation should fail before editing task2.txt")

    def test_validation_passes_after_edit(self):
        """Test that validation passes after task2.txt is correctly edited."""
        self.vimtut.setup_lesson(self.lesson)

        task2 = self.vimtut.workspace_dir / "task2.txt"
        with open(task2, 'w') as f:
            f.write("This is the second file (task2.txt) COMPLETED")

        success, message = self.vimtut.validate_lesson(self.lesson)
        self.assertTrue(success, f"Validation should pass after correct edit: {message}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
