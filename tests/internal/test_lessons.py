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

# Import the Vimtut class from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from vimtut import Vimtut


class TestLessonContent(unittest.TestCase):
    """Test specific lessons have correct expected content."""

    def setUp(self):
        """Load all lessons."""
        self.vimtut = Vimtut()

    def test_lesson_02_navigation_delete_m(self):
        """Test lesson 2 - deleting 'M' produces correct output."""
        lesson = self.vimtut.get_lesson_by_id("navigation_hjkl")
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
        lesson = self.vimtut.get_lesson_by_id("insert_mode")
        self.assertIsNotNone(lesson)

        original = lesson['setup_file']
        expected = lesson['target_content']

        self.assertEqual(original, "The quick fox jumps over the lazy dog.")
        self.assertEqual(expected, "The quick brown fox jumps over the lazy dog.")

    def test_lesson_06_delete_extra_letters(self):
        """Test lesson 6 - deleting extra letters."""
        lesson = self.vimtut.get_lesson_by_id("delete_char")
        self.assertIsNotNone(lesson)

        original = lesson['setup_file']
        expected = lesson['target_content']

        self.assertEqual(original, "Helllllo Worrrlld")
        self.assertEqual(expected, "Hello World")

    def test_lesson_07_delete_lines(self):
        """Test lesson 7 - deleting specific lines."""
        lesson = self.vimtut.get_lesson_by_id("delete_line")
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
                          'validation_type', 'target_content', 'next_lesson']

        for lesson in self.vimtut.lessons:
            for field in required_fields:
                self.assertIn(field, lesson,
                             f"Lesson {lesson.get('id', 'unknown')} missing field: {field}")

    def test_validation_types_are_valid(self):
        """Ensure all lessons use valid validation types."""
        valid_types = ['file_saved', 'exact_match', 'contains', 'exact_match_file']

        for lesson in self.vimtut.lessons:
            validation_type = lesson.get('validation_type')
            self.assertIn(validation_type, valid_types,
                         f"Lesson {lesson['id']} has invalid validation_type: {validation_type}")


class TestLessonLinkedList(unittest.TestCase):
    """Test the linked list structure of lessons."""

    def setUp(self):
        """Load all lessons."""
        self.vimtut = Vimtut()

    def _load_all_lessons_raw(self, directory):
        """Load all lesson files from a directory into a dict by ID."""
        lessons_by_id = {}
        for lesson_file in directory.glob("*.json"):
            with open(lesson_file, 'r') as f:
                lesson = json.load(f)
                lessons_by_id[lesson['id']] = lesson
        return lessons_by_id

    def _validate_chain(self, lessons_by_id, chain_name):
        """Validate a lesson chain has no cycles and includes all lessons."""
        if not lessons_by_id:
            return  # Empty chain is valid

        # Find all IDs that are referenced as next_lesson
        all_ids = set(lessons_by_id.keys())
        referenced_ids = {
            lesson.get('next_lesson') 
            for lesson in lessons_by_id.values() 
            if lesson.get('next_lesson')
        }

        # Find the first lesson (not referenced by any other lesson)
        first_ids = all_ids - referenced_ids
        self.assertEqual(len(first_ids), 1,
            f"{chain_name}: Expected exactly 1 first lesson, found {len(first_ids)}: {first_ids}")

        first_id = first_ids.pop()

        # Walk the chain and check for cycles
        visited = set()
        current_id = first_id
        chain_order = []

        while current_id:
            self.assertNotIn(current_id, visited,
                f"{chain_name}: Cycle detected! '{current_id}' appears twice in chain. "
                f"Chain so far: {' -> '.join(chain_order)}")

            self.assertIn(current_id, lessons_by_id,
                f"{chain_name}: Lesson '{current_id}' referenced but not found in lessons")

            visited.add(current_id)
            chain_order.append(current_id)

            lesson = lessons_by_id[current_id]
            next_id = lesson.get('next_lesson')

            # If next_lesson is not None, it must exist
            if next_id is not None:
                self.assertIn(next_id, lessons_by_id,
                    f"{chain_name}: Lesson '{current_id}' references non-existent next_lesson '{next_id}'")

            current_id = next_id

        # All lessons should be visited (no orphans)
        orphans = all_ids - visited
        self.assertEqual(len(orphans), 0,
            f"{chain_name}: Found orphan lessons not in chain: {orphans}")

        # Chain length should match number of lessons
        self.assertEqual(len(chain_order), len(lessons_by_id),
            f"{chain_name}: Chain has {len(chain_order)} lessons but directory has {len(lessons_by_id)}")

    def test_basic_lessons_chain_valid(self):
        """Test that basic lessons form a valid linked list."""
        lessons_by_id = self._load_all_lessons_raw(self.vimtut.lessons_dir)
        self._validate_chain(lessons_by_id, "Basic lessons")

    def test_advanced_lessons_chain_valid(self):
        """Test that advanced lessons form a valid linked list."""
        if not self.vimtut.advanced_dir.exists():
            self.skipTest("No advanced lessons directory")
        lessons_by_id = self._load_all_lessons_raw(self.vimtut.advanced_dir)
        self._validate_chain(lessons_by_id, "Advanced lessons")

    def test_no_cross_chain_references(self):
        """Test that basic and advanced chains don't reference each other."""
        basic_ids = {lesson['id'] for lesson in self.vimtut.basic_lessons}
        advanced_ids = {lesson['id'] for lesson in self.vimtut.advanced_lessons}

        # Check basic lessons don't point to advanced lessons
        for lesson in self.vimtut.basic_lessons:
            next_id = lesson.get('next_lesson')
            if next_id:
                self.assertNotIn(next_id, advanced_ids,
                    f"Basic lesson '{lesson['id']}' points to advanced lesson '{next_id}'")

        # Check advanced lessons don't point to basic lessons
        for lesson in self.vimtut.advanced_lessons:
            next_id = lesson.get('next_lesson')
            if next_id:
                self.assertNotIn(next_id, basic_ids,
                    f"Advanced lesson '{lesson['id']}' points to basic lesson '{next_id}'")

    def test_chains_end_with_null(self):
        """Test that each chain ends with a lesson where next_lesson is null."""
        # Check basic chain
        if self.vimtut.basic_lessons:
            last_basic = self.vimtut.basic_lessons[-1]
            self.assertIsNone(last_basic.get('next_lesson'),
                f"Last basic lesson '{last_basic['id']}' should have next_lesson=null, "
                f"but has '{last_basic.get('next_lesson')}'")

        # Check advanced chain
        if self.vimtut.advanced_lessons:
            last_advanced = self.vimtut.advanced_lessons[-1]
            self.assertIsNone(last_advanced.get('next_lesson'),
                f"Last advanced lesson '{last_advanced['id']}' should have next_lesson=null, "
                f"but has '{last_advanced.get('next_lesson')}'")

    def test_all_next_lesson_references_exist(self):
        """Test that every next_lesson reference points to an existing lesson."""
        all_ids = {lesson['id'] for lesson in self.vimtut.lessons}

        for lesson in self.vimtut.lessons:
            next_id = lesson.get('next_lesson')
            if next_id is not None:
                self.assertIn(next_id, all_ids,
                    f"Lesson '{lesson['id']}' references non-existent next_lesson '{next_id}'")


if __name__ == '__main__':
    unittest.main(verbosity=2)
