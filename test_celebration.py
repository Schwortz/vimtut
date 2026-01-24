#!/usr/bin/env python3
"""
Test the completion celebration screen
"""

import sys
import curses
sys.path.insert(0, '.')
from dojo_app import VimDojo

def show_celebration_preview(stdscr):
    """Preview the celebration screen."""
    dojo = VimDojo()

    # Show instructions
    stdscr.clear()
    stdscr.addstr(0, 0, "This is a preview of the celebration screen you'll see")
    stdscr.addstr(1, 0, "when you complete all 20 lessons!")
    stdscr.addstr(3, 0, "Press any key to see it...")
    stdscr.refresh()
    stdscr.getch()

    # Show celebration
    dojo.show_completion_celebration(stdscr)

if __name__ == '__main__':
    print("Launching celebration preview...")
    curses.wrapper(show_celebration_preview)
    print("\nThat's what you'll see when you master all 20 lessons! 🎉")
