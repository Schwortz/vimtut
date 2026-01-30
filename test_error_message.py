#!/usr/bin/env python3
"""Test the improved error message"""

import sys
sys.path.insert(0, '.')
from vimtut import Vimtut

# Create a vimtut instance
vimtut = Vimtut()

# Get lesson 2
lesson = vimtut.get_lesson_by_id("02_navigation_hjkl")

# The file currently has M still there
vimtut.current_lesson_file = vimtut.workspace_dir / "current_task.txt"

# Run validation
success, message = vimtut.validate_lesson(lesson)

print("Success:", success)
print("\nError Message:")
print("=" * 60)
print(message)
print("=" * 60)
