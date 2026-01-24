#!/usr/bin/env python3
"""
Debug tool to compare expected vs actual content byte-by-byte
"""

import sys
import json

def show_detailed_diff(expected, got):
    """Show detailed character-by-character comparison."""
    print("\n=== DETAILED COMPARISON ===")
    print(f"Expected length: {len(expected)}")
    print(f"Got length: {len(got)}")
    print(f"Length difference: {len(got) - len(expected)}")

    print("\n=== BYTE REPRESENTATION ===")
    print("Expected bytes:", repr(expected))
    print("Got bytes:     ", repr(got))

    print("\n=== LINE BY LINE ===")
    expected_lines = expected.split('\n')
    got_lines = got.split('\n')

    print(f"Expected lines: {len(expected_lines)}")
    print(f"Got lines: {len(got_lines)}")

    max_lines = max(len(expected_lines), len(got_lines))
    for i in range(max_lines):
        exp_line = expected_lines[i] if i < len(expected_lines) else "<missing>"
        got_line = got_lines[i] if i < len(got_lines) else "<missing>"

        match = "✓" if exp_line == got_line else "✗"
        print(f"\nLine {i+1} {match}:")
        print(f"  Expected: {repr(exp_line)}")
        print(f"  Got:      {repr(got_line)}")

        if exp_line != got_line and exp_line != "<missing>" and got_line != "<missing>":
            # Character by character comparison
            max_len = max(len(exp_line), len(got_line))
            for j in range(max_len):
                exp_char = exp_line[j] if j < len(exp_line) else "<end>"
                got_char = got_line[j] if j < len(got_line) else "<end>"
                if exp_char != got_char:
                    print(f"    Diff at position {j}: expected {repr(exp_char)}, got {repr(got_char)}")

    print("\n=== TRAILING CONTENT ===")
    if expected.endswith('\n'):
        print("Expected ends with newline: YES")
    else:
        print("Expected ends with newline: NO")

    if got.endswith('\n'):
        print("Got ends with newline: YES")
    else:
        print("Got ends with newline: NO")

if __name__ == "__main__":
    # Load lesson 2
    with open('lessons/02_navigation_hjkl.json', 'r') as f:
        lesson = json.load(f)

    expected = lesson['target_content']

    # Check if current_task.txt exists
    import os
    task_file = 'workspace/current_task.txt'
    if os.path.exists(task_file):
        with open(task_file, 'r') as f:
            got = f.read()

        print("Comparing workspace/current_task.txt with lesson 2 expected content")
        show_detailed_diff(expected, got)
    else:
        print(f"File {task_file} does not exist")
        print("\nExpected content:")
        print(repr(expected))
