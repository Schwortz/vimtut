#!/usr/bin/env python3
"""Test the improved error message"""

import sys
sys.path.insert(0, '.')
from dojo_app import VimDojo

# Create a dojo instance
dojo = VimDojo()

# Get lesson 2
lesson = dojo.get_lesson_by_id("02_navigation_hjkl")

# The file currently has M still there
dojo.current_lesson_file = dojo.workspace_dir / "current_task.txt"

# Run validation
success, message = dojo.validate_lesson(lesson)

print("Success:", success)
print("\nError Message:")
print("=" * 60)
print(message)
print("=" * 60)
