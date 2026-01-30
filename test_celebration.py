#!/usr/bin/env python3
"""
Test the completion celebration screen
"""

import sys
import curses
sys.path.insert(0, '.')
from vimtut import Vimtut

def show_celebration_preview(stdscr):
    """Preview the celebration screens."""
    vimtut = Vimtut()

    # Show instructions
    stdscr.clear()
    stdscr.addstr(0, 0, "This script shows two celebration screens:")
    stdscr.addstr(2, 0, "1. ADVANCED UNLOCKED (after 20 basic lessons)")
    stdscr.addstr(3, 0, "2. ULTIMATE MASTERY (after all 27 lessons)")
    stdscr.addstr(5, 0, "Press any key to see the first one...")
    stdscr.refresh()
    stdscr.getch()

    # Show advanced unlock
    vimtut.show_advanced_unlock(stdscr)

    # Transition message
    stdscr.clear()
    stdscr.addstr(0, 0, "That was the ADVANCED UNLOCKED screen!")
    stdscr.addstr(2, 0, "Now let's see what you get when you complete")
    stdscr.addstr(3, 0, "ALL 27 lessons (basic + advanced)...")
    stdscr.addstr(5, 0, "Press any key to continue...")
    stdscr.refresh()
    stdscr.getch()

    # Show ultimate celebration
    vimtut.show_completion_celebration(stdscr)

if __name__ == '__main__':
    print("Launching celebration preview...")
    print("You'll see two screens:")
    print("  1. Advanced Unlocked (after 20 basic lessons)")
    print("  2. Ultimate Mastery (after all 27 lessons)")
    print()
    curses.wrapper(show_celebration_preview)
    print("\nThose are the celebration screens! 🎉")
    print("Complete all 27 lessons to see them for real!")
