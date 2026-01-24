#!/usr/bin/env python3
"""
Unit tests for Vim Dojo validation logic
"""

import os
import sys
import json
import time
import tempfile
import unittest
from pathlib import Path

# Import the VimDojo class
sys.path.insert(0, os.path.dirname(__file__))
from dojo_app import VimDojo


class TestVimDojoValidation(unittest.TestCase):
    """Test validation logic for different lesson types."""

    def setUp(self):
        """Set up test environment with temporary workspace."""
        self.test_dir = tempfile.mkdtemp()
        self.dojo = VimDojo()
        # Override workspace to use temp directory
        self.dojo.workspace_dir = Path(self.test_dir)
        self.dojo.current_lesson_file = self.dojo.workspace_dir / "current_task.txt"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_file_saved_validation_success(self):
        """Test that file_saved validation passes when file is actually saved."""
        lesson = {
            "id": "test_exit",
            "validation_type": "file_saved",
            "setup_file": "",
            "target_content": ""
        }

        # Setup the lesson (creates file and records mtime)
        self.dojo.setup_lesson(lesson)

        # Simulate Vim saving the file by sleeping and touching it
        time.sleep(0.01)  # Ensure time has passed
        with open(self.dojo.current_lesson_file, 'w') as f:
            f.write("")  # Write (simulating :wq)

        # Validate
        success, message = self.dojo.validate_lesson(lesson)
        self.assertTrue(success, f"Validation should pass: {message}")
        self.assertIn("Success", message)

    def test_file_saved_validation_failure_not_modified(self):
        """Test that file_saved validation fails when file is not modified."""
        lesson = {
            "id": "test_exit",
            "validation_type": "file_saved",
            "setup_file": "",
            "target_content": ""
        }

        # Setup the lesson
        self.dojo.setup_lesson(lesson)

        # Don't modify the file (simulating user just reading and closing)
        # File exists but mtime is unchanged

        # Validate
        success, message = self.dojo.validate_lesson(lesson)
        self.assertFalse(success, "Validation should fail when file not saved")
        self.assertIn("wasn't saved", message)

    def test_file_saved_validation_failure_file_deleted(self):
        """Test that file_saved validation fails when file is deleted (:q!)."""
        lesson = {
            "id": "test_exit",
            "validation_type": "file_saved",
            "setup_file": "",
            "target_content": ""
        }

        # Setup the lesson
        self.dojo.setup_lesson(lesson)

        # Delete the file (simulating :q! without saving)
        os.remove(self.dojo.current_lesson_file)

        # Validate
        success, message = self.dojo.validate_lesson(lesson)
        self.assertFalse(success, "Validation should fail when file deleted")
        self.assertIn("doesn't exist", message)

    def test_exact_match_validation_success(self):
        """Test exact_match validation with correct content."""
        lesson = {
            "id": "test_nav",
            "validation_type": "exact_match",
            "setup_file": "A B C\nD E F",
            "target_content": "A B C\nD   F"
        }

        # Setup
        self.dojo.setup_lesson(lesson)

        # Write the correct content
        with open(self.dojo.current_lesson_file, 'w') as f:
            f.write("A B C\nD   F")

        # Validate
        success, message = self.dojo.validate_lesson(lesson)
        self.assertTrue(success, f"Validation should pass: {message}")
        self.assertIn("Perfect", message)

    def test_exact_match_validation_failure(self):
        """Test exact_match validation with incorrect content."""
        lesson = {
            "id": "test_nav",
            "validation_type": "exact_match",
            "setup_file": "A B C",
            "target_content": "A B C"
        }

        # Setup
        self.dojo.setup_lesson(lesson)

        # Write wrong content
        with open(self.dojo.current_lesson_file, 'w') as f:
            f.write("A B X")  # Wrong!

        # Validate
        success, message = self.dojo.validate_lesson(lesson)
        self.assertFalse(success, "Validation should fail with wrong content")
        self.assertIn("Not quite right", message)
        self.assertIn("DIFFERENT", message)  # New improved message format

    def test_contains_validation_success(self):
        """Test contains validation when substring is present."""
        lesson = {
            "id": "test_contains",
            "validation_type": "contains",
            "setup_file": "Hello World",
            "target_content": "edited"
        }

        # Setup
        self.dojo.setup_lesson(lesson)

        # Add the required text
        with open(self.dojo.current_lesson_file, 'w') as f:
            f.write("Hello World - edited")

        # Validate
        success, message = self.dojo.validate_lesson(lesson)
        self.assertTrue(success, f"Validation should pass: {message}")
        self.assertIn("Great work", message)

    def test_contains_validation_failure(self):
        """Test contains validation when substring is missing."""
        lesson = {
            "id": "test_contains",
            "validation_type": "contains",
            "setup_file": "Hello World",
            "target_content": "edited"
        }

        # Setup
        self.dojo.setup_lesson(lesson)

        # Don't add the required text
        with open(self.dojo.current_lesson_file, 'w') as f:
            f.write("Hello World")  # Missing "edited"

        # Validate
        success, message = self.dojo.validate_lesson(lesson)
        self.assertFalse(success, "Validation should fail when substring missing")
        self.assertIn("should contain", message)

    def test_load_lessons(self):
        """Test that lessons are loaded correctly from JSON files."""
        # This uses the real lessons directory
        dojo = VimDojo()
        self.assertGreater(len(dojo.lessons), 0, "Should load lessons")

        # Check first lesson structure
        first_lesson = dojo.lessons[0]
        self.assertIn('id', first_lesson)
        self.assertIn('title', first_lesson)
        self.assertIn('validation_type', first_lesson)
        self.assertIn('instruction_text', first_lesson)

    def test_lesson_01_structure(self):
        """Test that lesson 01 (The Exit) has correct structure."""
        dojo = VimDojo()
        lesson = dojo.get_lesson_by_id("01_the_exit")

        self.assertIsNotNone(lesson, "Lesson 01 should exist")
        self.assertEqual(lesson['validation_type'], 'file_saved')
        self.assertEqual(lesson['setup_file'], '')


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestVimDojoValidation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
