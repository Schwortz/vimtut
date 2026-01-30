#!/usr/bin/env python3
"""
Test lesson 22 (multiple files) functionality
"""

import sys
sys.path.insert(0, '.')
from vimtut import Vimtut
import os

def test_lesson_22():
    """Test that lesson 22 properly creates and validates second file."""
    vimtut = Vimtut()
    lesson = vimtut.get_lesson_by_id("22_multiple_files")

    print("=" * 60)
    print("TESTING LESSON 22: Multiple Files")
    print("=" * 60)

    # Setup
    print("\n1. Setting up lesson...")
    vimtut.setup_lesson(lesson)

    # Check files created
    print("\n2. Checking files in workspace...")
    task1 = vimtut.workspace_dir / "current_task.txt"
    task2 = vimtut.workspace_dir / "task2.txt"

    if task1.exists():
        with open(task1, 'r') as f:
            content1 = f.read()
        print(f"   ✓ current_task.txt: {repr(content1)}")
    else:
        print("   ✗ current_task.txt NOT FOUND")

    if task2.exists():
        with open(task2, 'r') as f:
            content2 = f.read()
        print(f"   ✓ task2.txt: {repr(content2)}")
    else:
        print("   ✗ task2.txt NOT FOUND")

    # Test validation - before editing
    print("\n3. Testing validation BEFORE editing task2.txt...")
    success, message = vimtut.validate_lesson(lesson)
    print(f"   Result: {'✓ PASS' if success else '✗ FAIL'}")
    if not success:
        print(f"   Message: {message.split(chr(10))[0]}")  # First line only

    # Simulate user editing task2.txt
    print("\n4. Simulating user editing task2.txt...")
    with open(task2, 'w') as f:
        f.write("This is the second file (task2.txt) COMPLETED")
    print("   ✓ Added ' COMPLETED' to task2.txt")

    # Test validation - after editing
    print("\n5. Testing validation AFTER editing task2.txt...")
    success, message = vimtut.validate_lesson(lesson)
    print(f"   Result: {'✓ PASS' if success else '✗ FAIL'}")
    print(f"   Message: {message}")

    print("\n" + "=" * 60)
    if success:
        print("✅ Lesson 22 works correctly!")
        print("\nWhat the user experiences:")
        print("  1. Opens Vim with current_task.txt")
        print("  2. Types :e task2.txt to open second file")
        print("  3. Adds ' COMPLETED' to task2.txt")
        print("  4. Saves with :wq")
        print("  5. Validation checks task2.txt was edited ✓")
    else:
        print("❌ Lesson 22 validation failed")
    print("=" * 60)

if __name__ == '__main__':
    test_lesson_22()
