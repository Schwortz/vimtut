#!/usr/bin/env python3
"""
Test that lesson 22 cleanup works
"""

import sys
import os
sys.path.insert(0, '.')
from dojo_app import VimDojo

def test_cleanup():
    """Test that task2.txt is cleaned up after lesson."""
    dojo = VimDojo()
    lesson = dojo.get_lesson_by_id("22_multiple_files")

    print("Testing lesson 22 cleanup...")
    print()

    # Setup
    print("1. Setting up lesson...")
    dojo.setup_lesson(lesson)

    task2_path = dojo.workspace_dir / "task2.txt"

    # Check file exists
    if task2_path.exists():
        print("   ✓ task2.txt created")
    else:
        print("   ✗ task2.txt NOT created")
        return

    # Run cleanup
    print()
    print("2. Running cleanup...")
    dojo.cleanup_lesson(lesson)

    # Check file deleted
    if not task2_path.exists():
        print("   ✓ task2.txt deleted")
    else:
        print("   ✗ task2.txt still exists")

    print()
    print("3. Testing cleanup is automatic in run_lesson...")

    # Setup again
    dojo.setup_lesson(lesson)

    if task2_path.exists():
        print("   ✓ task2.txt created again")

    # Simulate user completing lesson
    with open(task2_path, 'w') as f:
        f.write("This is the second file (task2.txt) COMPLETED")

    # The cleanup should happen in finally block
    # We can't easily test the full run_lesson without TUI
    # But we can test cleanup directly
    dojo.cleanup_lesson(lesson)

    if not task2_path.exists():
        print("   ✓ task2.txt cleaned up after completion")
        print()
        print("✅ Cleanup works correctly!")
    else:
        print("   ✗ task2.txt not cleaned up")
        print()
        print("❌ Cleanup failed")

if __name__ == '__main__':
    test_cleanup()
