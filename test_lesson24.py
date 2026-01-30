#!/usr/bin/env python3
"""
Test lesson 24 (marks) functionality
"""

import sys
sys.path.insert(0, '.')
from dojo_app import VimDojo
import os

def test_lesson_24():
    """Test that lesson 24 properly creates a long file and validates mark usage."""
    dojo = VimDojo()
    lesson = dojo.get_lesson_by_id("24_marks")

    print("=" * 60)
    print("TESTING LESSON 24: Marks")
    print("=" * 60)

    # Setup
    print("\n1. Setting up lesson...")
    dojo.setup_lesson(lesson)

    # Check file created
    print("\n2. Checking file in workspace...")
    task_file = dojo.workspace_dir / "current_task.txt"

    if task_file.exists():
        with open(task_file, 'r') as f:
            content = f.read()

        word_count = len(content.split())
        delete_count = content.count('DELETE_THIS')
        line_count = len(content.split('\n'))

        print(f"   ✓ current_task.txt created")
        print(f"   ✓ Word count: {word_count} words")
        print(f"   ✓ Line count: {line_count} lines")
        print(f"   ✓ DELETE_THIS markers: {delete_count} found")

        if delete_count == 3:
            print("   ✓ Correct number of DELETE_THIS markers")
        else:
            print(f"   ✗ Expected 3 DELETE_THIS markers, found {delete_count}")
    else:
        print("   ✗ current_task.txt NOT FOUND")

    # Test validation - before editing
    print("\n3. Testing validation BEFORE removing DELETE_THIS...")
    success, message = dojo.validate_lesson(lesson)
    print(f"   Result: {'✓ PASS' if success else '✗ FAIL'}")
    if not success:
        print(f"   Message: {message.split(chr(10))[0]}")

    # Simulate user removing DELETE_THIS words
    print("\n4. Simulating user removing all DELETE_THIS words...")
    with open(task_file, 'r') as f:
        content = f.read()

    # Remove all DELETE_THIS occurrences
    content_cleaned = content.replace('DELETE_THIS ', '')

    with open(task_file, 'w') as f:
        f.write(content_cleaned)

    remaining = content_cleaned.count('DELETE_THIS')
    print(f"   ✓ Removed DELETE_THIS words")
    print(f"   ✓ Remaining DELETE_THIS: {remaining}")

    # Test validation - after editing
    print("\n5. Testing validation AFTER removing DELETE_THIS...")
    success, message = dojo.validate_lesson(lesson)
    print(f"   Result: {'✓ PASS' if success else '✗ FAIL'}")
    if success:
        print(f"   Message: {message}")
    else:
        # Show first few lines of diff
        lines = message.split('\n')
        for line in lines[:10]:
            print(f"   {line}")
        if len(lines) > 10:
            print(f"   ... ({len(lines) - 10} more lines)")

    # Test cleanup
    print("\n6. Testing cleanup...")
    dojo.cleanup_lesson(lesson)
    print("   ✓ Cleanup completed")

    print("\n" + "=" * 60)
    if success:
        print("✅ Lesson 24 works correctly!")
        print("\nWhat the user experiences:")
        print("  1. Opens Vim with a ~500 word document about text editors")
        print("  2. Types :marks to see pre-set marks a, b, c")
        print("  3. Jumps to mark a with 'a, deletes DELETE_THIS with daw")
        print("  4. Jumps to mark b with 'b, deletes DELETE_THIS with daw")
        print("  5. Jumps to mark c with 'c, deletes DELETE_THIS with daw")
        print("  6. Saves with :wq")
        print("  7. Validation checks all DELETE_THIS words removed ✓")
    else:
        print("❌ Lesson 24 validation failed")
    print("=" * 60)

if __name__ == '__main__':
    test_lesson_24()
