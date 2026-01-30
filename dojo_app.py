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
import argparse
from pathlib import Path
from typing import Dict, List, Optional


class VimDojo:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.lessons_dir = self.base_dir / "lessons"
        self.advanced_dir = self.lessons_dir / "advanced"
        self.workspace_dir = self.base_dir / "workspace"
        self.vimrc_path = self.workspace_dir / ".vimrc"
        self.current_lesson_file = self.workspace_dir / "current_task.txt"
        self.progress_file = self.base_dir / "progress.json"

        self.basic_lessons = self.load_lessons(self.lessons_dir, recursive=False)
        self.advanced_lessons = self.load_lessons(self.advanced_dir, recursive=False) if self.advanced_dir.exists() else []
        self.lessons = self.basic_lessons + self.advanced_lessons  # For compatibility
        self.completed_lessons = self.load_progress()
        self.current_mode = 'basic'  # 'basic' or 'advanced'

    def load_lessons(self, directory: Path, recursive: bool = False) -> List[Dict]:
        """Load lesson configurations from a directory."""
        lessons = []
        pattern = "**/*.json" if recursive else "*.json"
        for lesson_file in sorted(directory.glob(pattern)):
            with open(lesson_file, 'r') as f:
                lessons.append(json.load(f))
        return lessons

    def get_lesson_by_id(self, lesson_id: str) -> Optional[Dict]:
        """Get a specific lesson by its ID."""
        for lesson in self.lessons:
            if lesson['id'] == lesson_id:
                return lesson
        return None

    def load_progress(self) -> set:
        """Load user progress from file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('completed_lessons', []))
            except (json.JSONDecodeError, IOError):
                return set()
        return set()

    def save_progress(self):
        """Save user progress to file."""
        data = {
            'completed_lessons': list(self.completed_lessons),
            'total_lessons': len(self.lessons),
            'completion_percentage': int((len(self.completed_lessons) / len(self.lessons)) * 100)
        }
        with open(self.progress_file, 'w') as f:
            json.dump(data, f, indent=2)

    def setup_lesson(self, lesson: Dict):
        """Prepare the workspace for a lesson."""
        # Write the starting file content
        with open(self.current_lesson_file, 'w') as f:
            f.write(lesson['setup_file'])
        # Store the initial modification time
        self.file_mtime_before = os.path.getmtime(self.current_lesson_file)

        # Special setup for multiple files lesson (lesson 24)
        if lesson['id'] == '24_multiple_files':
            task2_file = self.workspace_dir / "task2.txt"
            with open(task2_file, 'w') as f:
                f.write("This is the second file (task2.txt)")
            # Store its mtime too for validation
            self.task2_mtime_before = os.path.getmtime(task2_file)

        # Special setup for split windows lesson (lesson 25)
        if lesson['id'] == '25_split_windows':
            section2_file = self.workspace_dir / "section2.txt"
            with open(section2_file, 'w') as f:
                f.write("=== TARGET FILE ===\n\nPassword: REPLACE_ME")

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

    def launch_vim(self, lesson: Dict = None):
        """Launch Vim with the tutorial configuration."""
        # Save terminal state
        curses.endwin()

        # Choose vimrc: use vertical split version for lesson 26 (marks)
        vimrc_to_use = self.vimrc_path
        if lesson and lesson['id'] == '26_marks':
            vimrc_to_use = self.workspace_dir / ".vimrc_vsplit"

        # Build command
        cmd = [
            'vim',
            '-u', str(vimrc_to_use),
        ]

        # Special handling for multiple files lesson (lesson 24)
        # Open both files so user can switch between them
        if lesson and lesson['id'] == '24_multiple_files':
            task2_file = self.workspace_dir / "task2.txt"
            cmd.append(str(self.current_lesson_file))
            cmd.append(str(task2_file))
        # Special handling for split windows lesson (lesson 25)
        # Open both files but don't auto-split (user must split)
        elif lesson and lesson['id'] == '25_split_windows':
            section2_file = self.workspace_dir / "section2.txt"
            cmd.append(str(self.current_lesson_file))
            cmd.append(str(section2_file))
        # Special handling for marks lesson (lesson 26)
        # Pre-set marks at DELETE_THIS positions
        elif lesson and lesson['id'] == '26_marks':
            cmd.append(str(self.current_lesson_file))
            # Execute commands to set marks at each DELETE_THIS occurrence
            cmd.extend([
                '-c', '/DELETE_THIS',  # Find first occurrence
                '-c', 'normal! ma',     # Set mark a
                '-c', 'silent! normal! n',  # Find next (silent to avoid error messages)
                '-c', 'normal! mb',     # Set mark b
                '-c', 'silent! normal! n',  # Find next
                '-c', 'normal! mc',     # Set mark c
                '-c', 'normal! gg',     # Go back to top
            ])
        else:
            cmd.append(str(self.current_lesson_file))

        # Run from workspace directory so relative paths work
        subprocess.run(cmd, cwd=str(self.workspace_dir))

        # Restore curses
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        return stdscr

    def validate_lesson(self, lesson: Dict) -> tuple[bool, str]:
        """Validate if the user completed the lesson correctly."""
        validation_type = lesson['validation_type']

        if validation_type == 'exact_match_file':
            # Special validation for multiple files lesson - check a different file
            validation_file = self.workspace_dir / lesson.get('validation_file', 'task2.txt')

            if not validation_file.exists():
                return False, f"The file '{lesson.get('validation_file')}' wasn't created or saved.\nDid you use ':e {lesson.get('validation_file')}' to open it?"

            with open(validation_file, 'r') as f:
                content = f.read()

            content_normalized = content.rstrip('\n')
            target_normalized = lesson['target_content'].rstrip('\n')

            if content_normalized == target_normalized:
                return True, "Perfect! You successfully edited the second file!"
            else:
                expected_lines = target_normalized.split('\n')
                got_lines = content_normalized.split('\n')

                diff_msg = "Not quite right. Check the second file (task2.txt).\n\n"
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

        elif validation_type == 'file_saved':
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

    def all_basic_lessons_complete(self) -> bool:
        """Check if all basic lessons are completed."""
        basic_ids = set(lesson['id'] for lesson in self.basic_lessons)
        return basic_ids.issubset(self.completed_lessons)

    def draw_menu(self, stdscr, selected_idx: int):
        """Draw the main lesson menu."""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Determine current lesson set
        current_lessons = self.basic_lessons if self.current_mode == 'basic' else self.advanced_lessons

        # Title
        mode_title = "BASIC" if self.current_mode == 'basic' else "ADVANCED"
        title = f"[ VIM DOJO - {mode_title} LESSONS ]"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)

        # Progress bar for current mode
        completed_in_mode = sum(1 for lesson in current_lessons if lesson['id'] in self.completed_lessons)
        progress_pct = int((completed_in_mode / len(current_lessons)) * 100) if current_lessons else 0
        progress_text = f"Progress: {completed_in_mode}/{len(current_lessons)} ({progress_pct}%)"
        stdscr.addstr(1, (width - len(progress_text)) // 2, progress_text)
        stdscr.addstr(2, 0, "-" * width)

        # Lessons for current mode
        for idx, lesson in enumerate(current_lessons):
            y = 4 + idx
            completed = lesson['id'] in self.completed_lessons
            checkbox = "[x]" if completed else "[ ]"

            # Get lesson number (extract from ID like "21_macros" -> 21)
            lesson_num = int(lesson['id'].split('_')[0])
            prefix = f"{checkbox} {lesson_num}. "
            lesson_text = f"{prefix}{lesson['title']}"

            if idx == selected_idx:
                lesson_text += " (Current)"
                stdscr.addstr(y, 2, lesson_text, curses.A_REVERSE)
            else:
                stdscr.addstr(y, 2, lesson_text)

        # Instructions
        y = 6 + len(current_lessons)
        stdscr.addstr(y, 0, "-" * width)
        stdscr.addstr(y + 1, 2, "Press ENTER to start lesson")
        stdscr.addstr(y + 2, 2, "Press 'q' to quit")
        stdscr.addstr(y + 3, 2, "Use UP/DOWN arrows or j/k to navigate")

        # Show mode switch option
        if self.current_mode == 'basic' and self.all_basic_lessons_complete():
            stdscr.addstr(y + 4, 2, "Press 'a' to access ADVANCED lessons", curses.A_BOLD)
        elif self.current_mode == 'advanced':
            stdscr.addstr(y + 4, 2, "Press 'b' to return to BASIC lessons")

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

    def cleanup_lesson(self, lesson: Dict):
        """Clean up any temporary files created for a lesson."""
        # Clean up task2.txt for multiple files lesson
        if lesson['id'] == '24_multiple_files':
            task2_file = self.workspace_dir / "task2.txt"
            if task2_file.exists():
                os.remove(task2_file)

        # Clean up section2.txt for split windows lesson
        if lesson['id'] == '25_split_windows':
            section2_file = self.workspace_dir / "section2.txt"
            if section2_file.exists():
                os.remove(section2_file)

    def run_lesson(self, stdscr, lesson: Dict):
        """Execute the full lesson cycle: vim -> verification -> debrief."""
        try:
            while True:
                # 1. Setup and launch Vim directly (no briefing screen)
                self.setup_lesson(lesson)
                stdscr = self.launch_vim(lesson)

                # 2. Validation
                success, message = self.validate_lesson(lesson)

                # 3. Debrief
                should_retry = self.draw_debrief(stdscr, success, message)

                if success:
                    self.completed_lessons.add(lesson['id'])
                    self.save_progress()

                    # Check if all basic lessons are complete (show unlock message)
                    if self.current_mode == 'basic' and self.all_basic_lessons_complete():
                        all_lessons_complete = len(self.completed_lessons) == len(self.lessons)
                        if not all_lessons_complete:
                            self.show_advanced_unlock(stdscr)

                    # Check if ALL lessons (basic + advanced) are complete
                    if len(self.completed_lessons) == len(self.lessons):
                        self.show_completion_celebration(stdscr)
                    break
                elif not should_retry:
                    # User chose to return to menu without completing
                    break
        finally:
            # Always clean up lesson files
            self.cleanup_lesson(lesson)

    def main_loop(self, stdscr):
        """Main TUI loop."""
        curses.curs_set(0)
        stdscr.keypad(True)

        selected_idx = 0

        while True:
            current_lessons = self.basic_lessons if self.current_mode == 'basic' else self.advanced_lessons

            self.draw_menu(stdscr, selected_idx)

            key = stdscr.getch()

            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('a') or key == ord('A'):
                # Switch to advanced mode (only if basics complete)
                if self.current_mode == 'basic' and self.all_basic_lessons_complete():
                    self.current_mode = 'advanced'
                    selected_idx = 0
            elif key == ord('b') or key == ord('B'):
                # Switch to basic mode
                if self.current_mode == 'advanced':
                    self.current_mode = 'basic'
                    selected_idx = 0
            elif key == curses.KEY_UP or key == ord('k') or key == ord('K'):
                selected_idx = max(0, selected_idx - 1)
            elif key == curses.KEY_DOWN or key == ord('j') or key == ord('J'):
                selected_idx = min(len(current_lessons) - 1, selected_idx + 1)
            elif key == ord('\n') or key == curses.KEY_ENTER:
                if selected_idx < len(current_lessons):
                    lesson = current_lessons[selected_idx]
                    self.run_lesson(stdscr, lesson)

    def show_advanced_unlock(self, stdscr):
        """Show message when advanced lessons are unlocked."""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        message = [
            "",
            "  ███████╗██╗  ██╗ ██████╗███████╗██╗     ██╗     ███████╗███╗   ██╗████████╗██╗",
            "  ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║     ██║     ██╔════╝████╗  ██║╚══██╔══╝██║",
            "  █████╗   ╚███╔╝ ██║     █████╗  ██║     ██║     █████╗  ██╔██╗ ██║   ██║   ██║",
            "  ██╔══╝   ██╔██╗ ██║     ██╔══╝  ██║     ██║     ██╔══╝  ██║╚██╗██║   ██║   ╚═╝",
            "  ███████╗██╔╝ ██╗╚██████╗███████╗███████╗███████╗███████╗██║ ╚████║   ██║   ██╗",
            "  ╚══════╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝",
            "",
            "            🎓 You've completed all BASIC lessons! 🎓",
            "",
            "              ADVANCED LESSONS are now unlocked!",
            "",
            "         Press 'a' in the main menu to access advanced topics:",
            "              • Macros          • Marks",
            "              • Multiple files  • Registers",
            "              • Split windows   • Find & Replace",
            "                      • Code Folding",
            "",
            "                   Ready for the next level?",
            "",
        ]

        start_y = max(0, (height - len(message)) // 2)
        for idx, line in enumerate(message):
            if start_y + idx < height:
                x = max(0, (width - len(line)) // 2)
                try:
                    stdscr.addstr(start_y + idx, x, line, curses.A_BOLD)
                except curses.error:
                    pass

        footer = "Press any key to continue"
        stdscr.addstr(height - 2, (width - len(footer)) // 2, footer)

        stdscr.refresh()
        stdscr.getch()

    def show_completion_celebration(self, stdscr):
        """Show a celebration screen when all lessons are complete."""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # ASCII art celebration
        celebration = [
            "",
            "  ██████╗ ██████╗ ███╗   ██╗ ██████╗ ██████╗  █████╗ ████████╗███████╗██╗",
            " ██╔════╝██╔═══██╗████╗  ██║██╔════╝ ██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██║",
            " ██║     ██║   ██║██╔██╗ ██║██║  ███╗██████╔╝███████║   ██║   ███████╗██║",
            " ██║     ██║   ██║██║╚██╗██║██║   ██║██╔══██╗██╔══██║   ██║   ╚════██║╚═╝",
            " ╚██████╗╚██████╔╝██║ ╚████║╚██████╔╝██║  ██║██║  ██║   ██║   ███████║██╗",
            "  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝",
            "",
            "                🎉  YOU'VE MASTERED VIM!  🎉",
            "",
            "           You've completed ALL 29 lessons!",
            "              (22 Basic + 7 Advanced)",
            "",
            "            You are now a true Vim master.",
            "          Go forth and edit with ultimate power!",
            "",
            "                    ⚡ ⚡ ⚡ ⚡ ⚡",
            "",
        ]

        # Center and display celebration
        start_y = max(0, (height - len(celebration)) // 2)
        for idx, line in enumerate(celebration):
            if start_y + idx < height:
                x = max(0, (width - len(line)) // 2)
                try:
                    stdscr.addstr(start_y + idx, x, line, curses.A_BOLD)
                except curses.error:
                    pass  # Ignore if line doesn't fit

        # Add footer
        footer = "Press any key to return to menu"
        stdscr.addstr(height - 2, (width - len(footer)) // 2, footer)

        stdscr.refresh()
        stdscr.getch()

    def run(self):
        """Start the Vim Dojo application."""
        curses.wrapper(self.main_loop)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Vim Dojo - Interactive Vim Tutorial',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./dojo_app.py                  Run normally
  ./dojo_app.py --progress 5     Fake completion of first 5 lessons
  ./dojo_app.py --progress 20    Fake completion of all 20 lessons (see celebration!)
  ./dojo_app.py --reset          Reset all progress
        """
    )
    parser.add_argument(
        '--progress',
        type=int,
        metavar='N',
        help='Fake completion of first N lessons (for testing)'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset all progress and start fresh'
    )

    args = parser.parse_args()

    # Check if vim is available
    if not os.path.exists('vim'):
        result = subprocess.run(['which', 'vim'], capture_output=True)
        if result.returncode != 0:
            print("Error: Vim is not installed or not in PATH.")
            print("Please install Vim to use Vim Dojo.")
            sys.exit(1)

    dojo = VimDojo()

    # Handle --reset flag
    if args.reset:
        if dojo.progress_file.exists():
            os.remove(dojo.progress_file)
            print("✓ Progress reset! All lessons marked as incomplete.")
        else:
            print("✓ No progress file found. Starting fresh.")
        sys.exit(0)

    # Handle --progress flag
    if args.progress is not None:
        n = args.progress
        if n < 0:
            print(f"Error: --progress value must be positive (got {n})")
            sys.exit(1)
        if n > len(dojo.lessons):
            print(f"Warning: --progress {n} exceeds total lessons ({len(dojo.lessons)})")
            print(f"Setting progress to {len(dojo.lessons)} instead.")
            n = len(dojo.lessons)

        # Mark first N lessons as complete
        dojo.completed_lessons = set(lesson['id'] for lesson in dojo.lessons[:n])
        dojo.save_progress()

        print(f"✓ Faked completion of first {n} lessons!")
        print(f"  Progress: {n}/{len(dojo.lessons)} ({int((n/len(dojo.lessons))*100)}%)")

        if n == len(dojo.lessons):
            print("\n🎉 All lessons marked complete! Launch the app to see the celebration!")

        sys.exit(0)

    # Run normally
    dojo.run()


if __name__ == "__main__":
    main()
