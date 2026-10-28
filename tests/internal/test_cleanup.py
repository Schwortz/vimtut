#!/usr/bin/env python3
"""Test that lesson cleanup works properly.

Run directly or via ``tests/run_all_tests.py``.
"""

import os
import sys
import unittest
from typing import Any

# Import the Vimtut class from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from vimtut import Vimtut


class TestLessonCleanup(unittest.TestCase):
    """Test cleanup functionality for lessons with extra files."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.vimtut = Vimtut()

    def test_multiple_files_cleanup(self) -> None:
        """Test that task2.txt is cleaned up after multiple_files lesson."""
        lesson: dict[str, Any] = self.vimtut.get_lesson_by_id("multiple_files")  # type: ignore[assignment]  # asserted non-None below
        self.assertIsNotNone(lesson, "Lesson 'multiple_files' should exist")

        # Setup the lesson
        self.vimtut.setup_lesson(lesson)

        task2_path = self.vimtut.workspace_dir / "task2.txt"

        # Check file exists after setup
        self.assertTrue(task2_path.exists(), "task2.txt should be created during setup")

        # Run cleanup
        self.vimtut.cleanup_lesson(lesson)

        # Check file is deleted
        self.assertFalse(task2_path.exists(), "task2.txt should be deleted after cleanup")

    def test_split_windows_cleanup(self) -> None:
        """Test that section2.txt is cleaned up after split_windows lesson."""
        lesson: dict[str, Any] = self.vimtut.get_lesson_by_id("split_windows")  # type: ignore[assignment]  # asserted non-None below
        self.assertIsNotNone(lesson, "Lesson 'split_windows' should exist")

        # Setup the lesson
        self.vimtut.setup_lesson(lesson)

        section2_path = self.vimtut.workspace_dir / "section2.txt"

        # Check file exists after setup
        self.assertTrue(section2_path.exists(), "section2.txt should be created during setup")

        # Run cleanup
        self.vimtut.cleanup_lesson(lesson)

        # Check file is deleted
        self.assertFalse(section2_path.exists(), "section2.txt should be deleted after cleanup")


if __name__ == '__main__':
    unittest.main(verbosity=2)
