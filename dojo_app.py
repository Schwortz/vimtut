#!/usr/bin/env python3
"""
Vim Dojo - Interactive Vim Tutorial
A TUI wrapper that teaches Vim through hands-on lessons
"""

import os
import sys
import json
import curses
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional


class VimDojo:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.lessons_dir = self.base_dir / "lessons"
        self.workspace_dir = self.base_dir / "workspace"
        self.vimrc_path = self.workspace_dir / ".vimrc"
        self.current_lesson_file = self.workspace_dir / "current_task.txt"

        self.lessons = self.load_lessons()
        self.completed_lessons = set()

    def load_lessons(self) -> List[Dict]:
        """Load all lesson configurations from the lessons directory."""
        lessons = []
        for lesson_file in sorted(self.lessons_dir.glob("*.json")):
            with open(lesson_file, 'r') as f:
                lessons.append(json.load(f))
        return lessons

    def get_lesson_by_id(self, lesson_id: str) -> Optional[Dict]:
        """Get a specific lesson by its ID."""
        for lesson in self.lessons:
            if lesson['id'] == lesson_id:
                return lesson
        return None

    def setup_lesson(self, lesson: Dict):
        """Prepare the workspace for a lesson."""
        # Write the starting file content
        with open(self.current_lesson_file, 'w') as f:
            f.write(lesson['setup_file'])
        # Store the initial modification time
        self.file_mtime_before = os.path.getmtime(self.current_lesson_file)

        # Create instructions file for Vim split view (only if lesson has full metadata)
        if 'title' in lesson and 'instruction_text' in lesson:
            instructions_file = self.workspace_dir / "instructions.txt"
            with open(instructions_file, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write(f"LESSON: {lesson['title']}\n")
                f.write("=" * 70 + "\n")
                f.write(lesson['instruction_text'])
                f.write("\n" + "=" * 70 + "\n")
                f.write("This pane is READ-ONLY. Edit in the pane above.\n")
                f.write("=" * 70 + "\n")  # Add trailing newline to avoid "Incomplete last line"

    def launch_vim(self):
        """Launch Vim with the tutorial configuration."""
        # Save terminal state
        curses.endwin()

        # Launch Vim with custom config
        cmd = [
            'vim',
            '-u', str(self.vimrc_path),
            str(self.current_lesson_file)
        ]

        subprocess.run(cmd)

        # Restore curses
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        return stdscr

    def validate_lesson(self, lesson: Dict) -> tuple[bool, str]:
        """Validate if the user completed the lesson correctly."""
        validation_type = lesson['validation_type']

        if validation_type == 'file_saved':
            # Check if file exists and was modified (saved)
            if not self.current_lesson_file.exists():
                return False, "The file doesn't exist. Did you use :q! instead of :wq?"

            # Check if file was modified after we created it
            file_mtime_after = os.path.getmtime(self.current_lesson_file)
            if file_mtime_after > self.file_mtime_before:
                return True, "Success! You've learned how to exit Vim with :wq"
            else:
                return False, "The file wasn't saved. Make sure to use :wq (not :q!)"

        elif validation_type == 'exact_match':
            # Check if file content matches target
            if not self.current_lesson_file.exists():
                return False, "The file wasn't saved."

            with open(self.current_lesson_file, 'r') as f:
                content = f.read()

            # Normalize: strip trailing whitespace/newlines that Vim adds
            # This is standard for text file comparison
            content_normalized = content.rstrip('\n')
            target_normalized = lesson['target_content'].rstrip('\n')

            if content_normalized == target_normalized:
                return True, "Perfect! You completed the task correctly."
            else:
                # Show detailed diff to help user understand what's wrong
                expected_lines = target_normalized.split('\n')
                got_lines = content_normalized.split('\n')

                diff_msg = "Not quite right. Try again.\n\n"
                diff_msg += "Line-by-line comparison:\n"

                for i in range(max(len(expected_lines), len(got_lines))):
                    exp = expected_lines[i] if i < len(expected_lines) else "<missing>"
                    got = got_lines[i] if i < len(got_lines) else "<missing>"

                    if exp == got:
                        diff_msg += f"Line {i+1}: OK\n"
                    else:
                        diff_msg += f"Line {i+1}: DIFFERENT\n"
                        diff_msg += f"  Expected: [{exp}]\n"
                        diff_msg += f"  Got:      [{got}]\n"

                return False, diff_msg

        elif validation_type == 'contains':
            # Check if file contains specific string
            if not self.current_lesson_file.exists():
                return False, "The file wasn't saved."

            with open(self.current_lesson_file, 'r') as f:
                content = f.read()

            if lesson['target_content'] in content:
                return True, "Great work! You've completed the lesson."
            else:
                return False, f"The file should contain: {lesson['target_content']}"

        return False, "Unknown validation type"

    def draw_menu(self, stdscr, selected_idx: int):
        """Draw the main lesson menu."""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Title
        title = "[ VIM DOJO ]"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        stdscr.addstr(1, 0, "-" * width)

        # Lessons
        for idx, lesson in enumerate(self.lessons):
            y = 3 + idx
            completed = lesson['id'] in self.completed_lessons
            checkbox = "[x]" if completed else "[ ]"
            prefix = f"{checkbox} {idx + 1}. "
            lesson_text = f"{prefix}{lesson['title']}"

            if idx == selected_idx:
                lesson_text += " (Current)"
                stdscr.addstr(y, 2, lesson_text, curses.A_REVERSE)
            else:
                stdscr.addstr(y, 2, lesson_text)

        # Instructions
        y = 5 + len(self.lessons)
        stdscr.addstr(y, 0, "-" * width)
        stdscr.addstr(y + 1, 2, "Press ENTER to start lesson")
        stdscr.addstr(y + 2, 2, "Press 'q' to quit")
        stdscr.addstr(y + 3, 2, "Use UP/DOWN arrows or j/k to navigate")

        stdscr.refresh()

    def draw_briefing(self, stdscr, lesson: Dict) -> bool:
        """Display lesson briefing before launching Vim.
        Returns True to continue, False to abort."""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = f"LESSON: {lesson['title']}"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        stdscr.addstr(1, 0, "=" * width)

        # Simple message
        msg_lines = [
            "",
            "Instructions will appear in a split pane inside Vim.",
            "",
            "The instructions are in the BOTTOM pane (read-only).",
            "Your editable file is in the TOP pane.",
            "",
            "Use Ctrl+j to move to instructions pane.",
            "Use Ctrl+k to move back to edit pane.",
            "",
            "Save and quit with :wq when done.",
        ]

        for idx, line in enumerate(msg_lines):
            if idx + 3 < height - 5:
                stdscr.addstr(idx + 3, 2, line)

        # Prompt
        y = height - 3
        stdscr.addstr(y, 0, "-" * width)
        stdscr.addstr(y + 1, 2, "Press ENTER to launch Vim | Press ESC or 'q' to go back", curses.A_BOLD)

        stdscr.refresh()
        key = stdscr.getch()

        # Return False if user wants to abort (ESC or 'q')
        if key == 27 or key == ord('q') or key == ord('Q'):  # 27 is ESC
            return False
        return True

    def draw_debrief(self, stdscr, success: bool, message: str) -> bool:
        """Display lesson results after validation.
        Returns True to retry, False to return to menu."""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if success:
            title = "SUCCESS!"
            stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        else:
            title = "TRY AGAIN"
            stdscr.addstr(0, (width - len(title)) // 2, title)

        stdscr.addstr(1, 0, "=" * width)

        # Message
        lines = message.split('\n')
        for idx, line in enumerate(lines):
            if idx + 3 < height - 5:
                stdscr.addstr(idx + 3, 2, line)

        # Prompt
        y = height - 3
        stdscr.addstr(y, 0, "-" * width)
        if success:
            stdscr.addstr(y + 1, 2, "Press ENTER to return to menu", curses.A_BOLD)
        else:
            stdscr.addstr(y + 1, 2, "Press ENTER to try again | Press ESC or 'q' to go back", curses.A_BOLD)

        stdscr.refresh()
        key = stdscr.getch()

        # If failed and user presses ESC or 'q', return to menu
        if not success and (key == 27 or key == ord('q') or key == ord('Q')):
            return False
        return True

    def run_lesson(self, stdscr, lesson: Dict):
        """Execute the full lesson cycle: vim -> verification -> debrief."""
        while True:
            # 1. Setup and launch Vim directly (no briefing screen)
            self.setup_lesson(lesson)
            stdscr = self.launch_vim()

            # 2. Validation
            success, message = self.validate_lesson(lesson)

            # 3. Debrief
            should_retry = self.draw_debrief(stdscr, success, message)

            if success:
                self.completed_lessons.add(lesson['id'])
                break
            elif not should_retry:
                # User chose to return to menu without completing
                break

    def main_loop(self, stdscr):
        """Main TUI loop."""
        curses.curs_set(0)
        stdscr.keypad(True)

        selected_idx = 0

        while True:
            self.draw_menu(stdscr, selected_idx)

            key = stdscr.getch()

            if key == ord('q') or key == ord('Q'):
                break
            elif key == curses.KEY_UP or key == ord('k') or key == ord('K'):
                selected_idx = max(0, selected_idx - 1)
            elif key == curses.KEY_DOWN or key == ord('j') or key == ord('J'):
                selected_idx = min(len(self.lessons) - 1, selected_idx + 1)
            elif key == ord('\n') or key == curses.KEY_ENTER:
                lesson = self.lessons[selected_idx]
                self.run_lesson(stdscr, lesson)

    def run(self):
        """Start the Vim Dojo application."""
        curses.wrapper(self.main_loop)


def main():
    if not os.path.exists('vim'):
        # Check if vim is available
        result = subprocess.run(['which', 'vim'], capture_output=True)
        if result.returncode != 0:
            print("Error: Vim is not installed or not in PATH.")
            print("Please install Vim to use Vim Dojo.")
            sys.exit(1)

    dojo = VimDojo()
    dojo.run()


if __name__ == "__main__":
    main()
