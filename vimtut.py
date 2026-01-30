#!/usr/bin/env python3
"""
Vimtut - Interactive Vim Tutorial
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


class Vimtut:
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
        self.completed_lessons, self.welcome_seen = self.load_progress()
        self.current_mode = 'basic'  # 'basic' or 'advanced'

    def load_lessons(self, directory: Path, recursive: bool = False) -> List[Dict]:
        """Load lesson configurations from a directory and order by next_lesson chain."""
        # First, load all lessons into a dict by ID
        lessons_by_id = {}
        pattern = "**/*.json" if recursive else "*.json"
        for lesson_file in directory.glob(pattern):
            with open(lesson_file, 'r') as f:
                lesson = json.load(f)
                lessons_by_id[lesson['id']] = lesson
        
        if not lessons_by_id:
            return []
        
        # Find the first lesson (one that no other lesson points to)
        all_ids = set(lessons_by_id.keys())
        referenced_ids = {lesson.get('next_lesson') for lesson in lessons_by_id.values() if lesson.get('next_lesson')}
        first_ids = all_ids - referenced_ids
        
        if not first_ids:
            # Fallback: just return lessons in any order if chain is broken
            return list(lessons_by_id.values())
        
        # Build ordered list by following the chain
        ordered_lessons = []
        current_id = first_ids.pop()  # Start with the first lesson
        visited = set()
        
        while current_id and current_id in lessons_by_id:
            if current_id in visited:
                break  # Prevent infinite loops
            visited.add(current_id)
            lesson = lessons_by_id[current_id]
            ordered_lessons.append(lesson)
            current_id = lesson.get('next_lesson')
        
        # Add any lessons not in the chain (orphans) at the end
        for lesson_id, lesson in lessons_by_id.items():
            if lesson_id not in visited:
                ordered_lessons.append(lesson)
        
        return ordered_lessons

    def get_lesson_by_id(self, lesson_id: str) -> Optional[Dict]:
        """Get a specific lesson by its ID."""
        for lesson in self.lessons:
            if lesson['id'] == lesson_id:
                return lesson
        return None

    def load_progress(self) -> tuple:
        """Load user progress from file. Returns (completed_lessons, welcome_seen)."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('completed_lessons', [])), data.get('welcome_seen', False)
            except (json.JSONDecodeError, IOError):
                return set(), False
        return set(), False

    def save_progress(self):
        """Save user progress to file."""
        data = {
            'completed_lessons': list(self.completed_lessons),
            'total_lessons': len(self.lessons),
            'completion_percentage': int((len(self.completed_lessons) / len(self.lessons)) * 100),
            'welcome_seen': self.welcome_seen
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

        # Special setup for multiple files lesson
        if lesson['id'] == 'multiple_files':
            task2_file = self.workspace_dir / "task2.txt"
            with open(task2_file, 'w') as f:
                f.write("This is the second file (task2.txt)")
            # Store its mtime too for validation
            self.task2_mtime_before = os.path.getmtime(task2_file)

        # Special setup for split windows lesson
        if lesson['id'] == 'split_windows':
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
        curses.reset_shell_mode()

        # Choose vimrc: use vertical split version for marks lesson
        vimrc_to_use = self.vimrc_path
        if lesson and lesson['id'] == 'marks':
            vimrc_to_use = self.workspace_dir / ".vimrc_vsplit"

        # Build command
        cmd = [
            'vim',
            '-u', str(vimrc_to_use),
        ]

        # Special handling for multiple files lesson
        # Open both files so user can switch between them
        if lesson and lesson['id'] == 'multiple_files':
            task2_file = self.workspace_dir / "task2.txt"
            cmd.append(str(self.current_lesson_file))
            cmd.append(str(task2_file))
        # Special handling for split windows lesson
        # Open both files but don't auto-split (user must split)
        elif lesson and lesson['id'] == 'split_windows':
            section2_file = self.workspace_dir / "section2.txt"
            cmd.append(str(self.current_lesson_file))
            cmd.append(str(section2_file))
        # Special handling for marks lesson
        # Pre-set marks at FIXME positions using explicit line/column
        elif lesson and lesson['id'] == 'marks':
            cmd.append(str(self.current_lesson_file))
            # Set marks at specific lines, column 8 (where FIXME starts)
            # Line 5: FIXME in apples, Line 11: FIXME in bananas, Line 17: FIXME in cherries
            cmd.extend([
                '-c 5normal! 9|ma',
                '-c 11normal! 9|mb',
                '-c 17normal! 9|mc',
            ])
        else:
            cmd.append(str(self.current_lesson_file))

        # Run from workspace directory so relative paths work
        subprocess.run(cmd, cwd=str(self.workspace_dir))

        # Restore curses
        curses.reset_prog_mode()
        stdscr = curses.initscr()
        stdscr.keypad(True)
        stdscr.clear()
        stdscr.refresh()

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

    def draw_menu(self, stdscr, selected_idx: int, count_buffer: str = "", pending_g: bool = False):
        """Draw the main lesson menu."""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Determine current lesson set
        current_lessons = self.basic_lessons if self.current_mode == 'basic' else self.advanced_lessons

        # Title
        mode_title = "BASIC" if self.current_mode == 'basic' else "ADVANCED"
        title = f"[ VIMTUT - {mode_title} LESSONS ]"
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

            # Calculate lesson number based on position
            # Basic: 1, 2, 3... Advanced: continues from basic (e.g., 23, 24, 25...)
            if self.current_mode == 'basic':
                lesson_num = idx + 1
            else:
                lesson_num = len(self.basic_lessons) + idx + 1
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
        stdscr.addstr(y + 3, 2, "j/k to navigate, gg/G to jump, {N}gg to go to line N")

        # Show mode switch option
        if self.current_mode == 'basic' and self.all_basic_lessons_complete():
            stdscr.addstr(y + 4, 2, "Press 'a' to access ADVANCED lessons", curses.A_BOLD)
        elif self.current_mode == 'advanced':
            stdscr.addstr(y + 4, 2, "Press 'b' to return to BASIC lessons")

        # Show count buffer if user is typing a number
        if count_buffer or pending_g:
            indicator = count_buffer
            if pending_g:
                indicator += "g"
            stdscr.addstr(height - 1, 0, f":{indicator}", curses.A_BOLD)

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
        if lesson['id'] == 'multiple_files':
            task2_file = self.workspace_dir / "task2.txt"
            if task2_file.exists():
                os.remove(task2_file)

        # Clean up section2.txt for split windows lesson
        if lesson['id'] == 'split_windows':
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

    def handle_goto_key(self, key: int, count_buffer: str, pending_g: bool, max_idx: int) -> tuple:
        """Handle Vim-style goto line input (gg, G, {N}gg, {N}G).
        
        Returns: (handled, new_count_buffer, new_pending_g, target_idx or None)
        - handled: True if this key was consumed by goto logic
        - target_idx: The line to jump to, or None if no jump yet
        """
        # Handle digit input (0-9) - accumulate for count prefix
        if ord('0') <= key <= ord('9'):
            # Don't allow leading zeros
            if count_buffer or key != ord('0'):
                count_buffer += chr(key)
            return (True, count_buffer, False, None)

        # Handle 'g' key - first 'g' sets pending, second 'g' executes goto
        if key == ord('g'):
            if pending_g:
                # Second 'g' - execute goto
                if count_buffer:
                    target = int(count_buffer) - 1  # 1-indexed to 0-indexed
                    target = max(0, min(target, max_idx))
                else:
                    target = 0  # No count - go to first line
                return (True, "", False, target)
            else:
                # First 'g' - wait for second 'g'
                return (True, count_buffer, True, None)

        # Handle 'G' key - goto line N or last line
        if key == ord('G'):
            if count_buffer:
                target = int(count_buffer) - 1  # 1-indexed to 0-indexed
                target = max(0, min(target, max_idx))
            else:
                target = max_idx  # No count - go to last line
            return (True, "", False, target)

        # Key not handled by goto logic - clear state
        return (False, "", False, None)

    def show_welcome_screen(self, stdscr):
        """Show welcome screen on first launch. User must type :begin to continue."""
        curses.curs_set(1)  # Show cursor for typing
        stdscr.keypad(True)
        
        input_buffer = ""
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # ASCII art title
            title_art = [
                " ██╗   ██╗██╗███╗   ███╗████████╗██╗   ██╗████████╗",
                " ██║   ██║██║████╗ ████║╚══██╔══╝██║   ██║╚══██╔══╝",
                " ██║   ██║██║██╔████╔██║   ██║   ██║   ██║   ██║   ",
                " ╚██╗ ██╔╝██║██║╚██╔╝██║   ██║   ██║   ██║   ██║   ",
                "  ╚████╔╝ ██║██║ ╚═╝ ██║   ██║   ╚██████╔╝   ██║   ",
                "   ╚═══╝  ╚═╝╚═╝     ╚═╝   ╚═╝    ╚═════╝    ╚═╝   ",
            ]
            
            # Center and display title
            start_y = 2
            for idx, line in enumerate(title_art):
                x = max(0, (width - len(line)) // 2)
                try:
                    stdscr.addstr(start_y + idx, x, line, curses.A_BOLD)
                except curses.error:
                    pass
            
            # Welcome message
            messages = [
                "",
                "Welcome to Vimtut - Learn Vim the hands-on way!",
                "",
                "This interactive tutorial will teach you Vim through",
                "practical exercises. Each lesson includes:",
                "",
                "  - Clear instructions in a split pane",
                "  - A task file for you to edit",
                "  - Automatic validation of your work",
                "",
                "You'll start with basic navigation and progress to",
                "advanced features like macros, marks, and registers.",
                "",
                "Ready to begin your Vim journey?",
                "",
            ]
            
            msg_start_y = start_y + len(title_art) + 1
            for idx, line in enumerate(messages):
                if msg_start_y + idx < height - 4:
                    x = max(0, (width - len(line)) // 2)
                    try:
                        stdscr.addstr(msg_start_y + idx, x, line)
                    except curses.error:
                        pass
            
            # Command prompt
            prompt_y = height - 3
            stdscr.addstr(prompt_y - 1, 0, "-" * width)
            prompt_text = "Type :begin and press Enter to start"
            stdscr.addstr(prompt_y, (width - len(prompt_text)) // 2, prompt_text, curses.A_BOLD)
            
            # Input line (vim-style at bottom)
            input_y = height - 1
            stdscr.addstr(input_y, 0, ":" + input_buffer)
            stdscr.move(input_y, 1 + len(input_buffer))
            
            stdscr.refresh()
            
            key = stdscr.getch()
            
            if key == ord('\n') or key == curses.KEY_ENTER:
                if input_buffer == "begin":
                    self.welcome_seen = True
                    self.save_progress()
                    curses.curs_set(0)  # Hide cursor
                    return
                else:
                    input_buffer = ""  # Clear and try again
            elif key == 27:  # ESC - clear input
                input_buffer = ""
            elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
                input_buffer = input_buffer[:-1]
            elif key == ord(':'):  # Ignore extra colons
                pass
            elif 32 <= key <= 126:  # Printable characters
                input_buffer += chr(key)

    def main_loop(self, stdscr):
        """Main TUI loop."""
        curses.curs_set(0)
        stdscr.keypad(True)
        
        # Show welcome screen on first launch
        if not self.welcome_seen:
            self.show_welcome_screen(stdscr)

        selected_idx = 0
        count_buffer = ""  # Accumulates digits for count prefix (e.g., "15" in "15gg")
        pending_g = False  # True if 'g' was pressed, waiting for second 'g'

        while True:
            current_lessons = self.basic_lessons if self.current_mode == 'basic' else self.advanced_lessons
            max_idx = len(current_lessons) - 1

            self.draw_menu(stdscr, selected_idx, count_buffer, pending_g)

            key = stdscr.getch()

            # Handle Vim-style goto line navigation
            handled, count_buffer, pending_g, target_idx = self.handle_goto_key(
                key, count_buffer, pending_g, max_idx
            )
            if handled:
                if target_idx is not None:
                    selected_idx = target_idx
                continue

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
            elif key == curses.KEY_UP or key == ord('k'):
                selected_idx = max(0, selected_idx - 1)
            elif key == curses.KEY_DOWN or key == ord('j'):
                selected_idx = min(max_idx, selected_idx + 1)
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

        # Calculate counts dynamically
        total = len(self.lessons)
        basic = len(self.basic_lessons)
        advanced = len(self.advanced_lessons)

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
            f"           You've completed ALL {total} lessons!",
            f"              ({basic} Basic + {advanced} Advanced)",
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
        """Start the Vimtut application."""
        curses.wrapper(self.main_loop)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Vimtut - Interactive Vim Tutorial',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./vimtut.py                  Run normally
  ./vimtut.py --progress 5     Fake completion of first 5 lessons
  ./vimtut.py --progress 25    Fake completion of all basic lessons
  ./vimtut.py --reset          Reset all progress
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
            print("Please install Vim to use Vimtut.")
            sys.exit(1)

    vimtut = Vimtut()

    # Handle --reset flag
    if args.reset:
        if vimtut.progress_file.exists():
            os.remove(vimtut.progress_file)
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
        if n > len(vimtut.lessons):
            print(f"Warning: --progress {n} exceeds total lessons ({len(vimtut.lessons)})")
            print(f"Setting progress to {len(vimtut.lessons)} instead.")
            n = len(vimtut.lessons)

        # Mark first N lessons as complete
        vimtut.completed_lessons = set(lesson['id'] for lesson in vimtut.lessons[:n])
        vimtut.save_progress()

        print(f"✓ Faked completion of first {n} lessons!")
        print(f"  Progress: {n}/{len(vimtut.lessons)} ({int((n/len(vimtut.lessons))*100)}%)")

        if n == len(vimtut.lessons):
            print("\n🎉 All lessons marked complete! Launch the app to see the celebration!")

        sys.exit(0)

    # Run normally
    vimtut.run()


if __name__ == "__main__":
    main()
