#!/usr/bin/env python3
"""
Test lesson 23 (split windows) functionality
"""

import sys
sys.path.insert(0, '.')
from vimtut import Vimtut
import os

def test_lesson_23():
    """Test that lesson 23 properly creates and validates section2.txt."""
    vimtut = Vimtut()
    lesson = vimtut.get_lesson_by_id("23_split_windows")

    print("=" * 60)
    print("TESTING LESSON 23: Split Windows")
    print("=" * 60)

    # Setup
    print("\n1. Setting up lesson...")
    vimtut.setup_lesson(lesson)

    # Check files created
    print("\n2. Checking files in workspace...")
    task1 = vimtut.workspace_dir / "current_task.txt"
    section2 = vimtut.workspace_dir / "section2.txt"

    if task1.exists():
        with open(task1, 'r') as f:
            content1 = f.read()
        print(f"   ✓ current_task.txt: {repr(content1[:50])}")
    else:
        print("   ✗ current_task.txt NOT FOUND")

    if section2.exists():
        with open(section2, 'r') as f:
            content2 = f.read()
        print(f"   ✓ section2.txt: {repr(content2)}")
    else:
        print("   ✗ section2.txt NOT FOUND")

    # Test validation - before editing
    print("\n3. Testing validation BEFORE editing section2.txt...")
    success, message = vimtut.validate_lesson(lesson)
    print(f"   Result: {'✓ PASS' if success else '✗ FAIL'}")
    if not success:
        print(f"   Message: {message.split(chr(10))[0]}")

    # Simulate user editing section2.txt
    print("\n4. Simulating user copying SECRET CODE to section2.txt...")
    with open(section2, 'w') as f:
        f.write("=== TARGET FILE ===\n\nPassword: VimMaster$^&@")
    print("   ✓ Replaced 'REPLACE_ME' with 'VimMaster$^&@' in section2.txt")

    # Test validation - after editing
    print("\n5. Testing validation AFTER editing section2.txt...")
    success, message = vimtut.validate_lesson(lesson)
    print(f"   Result: {'✓ PASS' if success else '✗ FAIL'}")
    print(f"   Message: {message}")

    # Test cleanup
    print("\n6. Testing cleanup...")
    vimtut.cleanup_lesson(lesson)
    if not section2.exists():
        print("   ✓ section2.txt cleaned up")
    else:
        print("   ✗ section2.txt still exists")

    print("\n" + "=" * 60)
    if success:
        print("✅ Lesson 23 works correctly!")
        print("\nWhat the user experiences:")
        print("  1. Opens Vim with current_task.txt (SECRET CODE visible)")
        print("  2. Types :vsplit section2.txt to create split")
        print("  3. Sees both files side-by-side")
        print("  4. Copies 'VimMaster$^&@' from reference to section2.txt")
        print("  5. Saves with :wq")
        print("  6. Validation checks section2.txt has correct password ✓")
    else:
        print("❌ Lesson 23 validation failed")
    print("=" * 60)

if __name__ == '__main__':
    test_lesson_23()
