# Vimtut

An interactive TUI application that teaches Vim through hands-on lessons.

**32 Total Lessons:**
- 25 Basic Lessons (fundamentals)
- 7 Advanced Lessons (power-user features) - unlocked after basics!

## Architecture

Vimtut follows a "wrapper loop" pattern:

1. **Briefing (TUI)**: Quick overview before launching Vim
2. **Action (Vim)**: Launches real Vim with split-screen instructions
   - Top pane: Your editable file
   - Bottom pane: Read-only instructions (always visible!)
3. **Verification**: Validates the lesson completion when user exits Vim
4. **Debrief (TUI)**: Shows results and feedback

## Split Screen Feature

Instructions appear **inside Vim** as a bottom split pane:
- Instructions are always visible while you work
- Bottom pane is read-only (can't accidentally edit)
- Use **Ctrl+j** to view instructions, **Ctrl+k** to return to editing
- Immersive learning experience - everything in Vim!

## Directory Structure

```
vimtut/
├── vimtut.py        # Main TUI application
├── lessons/         # Lesson configurations (JSON)
│   ├── the_exit.json
│   ├── navigation_hjkl.json
│   └── ...          # Lessons linked via next_lesson field
├── workspace/       # User workspace
│   ├── .vimrc       # Custom Vim config for tutorials
│   └── current_task.txt  # Working file
└── README.md
```

## Requirements

- Python 3.6+
- Vim (must be installed and in PATH)

## Testing

Run the test suites to verify validation logic:

```bash
python3 test_validation.py   # Test validation logic
python3 test_lessons.py       # Test lesson content
```

All tests should pass before using the application.

## Debugging

If a lesson validation seems incorrect, use the debug tool:

```bash
python3 debug_validation.py
```

This shows byte-by-byte comparison of expected vs actual content.

## Usage

Run the tutorial:

```bash
./vimtut.py
```

Or:

```bash
python3 vimtut.py
```

## Controls

### Main Menu
- **UP/DOWN arrows** or **j/k**: Navigate lessons (Vim-style!)
- **ENTER**: Start selected lesson
- **q**: Quit application

### During Lessons (in TUI)
- **ESC** or **q**: Exit lesson and return to menu (at briefing or after failure)
- **ENTER**: Continue to next step or retry

### Inside Vim (during lesson)
- **Ctrl+j**: Move to instructions pane (bottom)
- **Ctrl+k**: Move back to edit pane (top)
- **:wq**: Save and quit (complete lesson)
- **:q!**: Quit without saving (lesson will fail)

## Adding New Lessons

Create a new JSON file in the `lessons/` directory:

```json
{
  "id": "lesson_id",
  "title": "Lesson Title",
  "instruction_text": "Instructions for the user",
  "setup_file": "Initial file content",
  "validation_type": "exact_match|file_saved|contains",
  "target_content": "Expected result",
  "next_lesson": "next_lesson_id"
}
```

Lessons are ordered via linked list - each lesson's `next_lesson` points to the next one.

### Validation Types

- `file_saved`: Checks if the file was saved (for exit lesson)
- `exact_match`: File content must exactly match `target_content`
- `contains`: File must contain `target_content` substring
