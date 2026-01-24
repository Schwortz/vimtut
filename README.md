# Vim Dojo

An interactive TUI application that teaches Vim through hands-on lessons.

## Architecture

Vim Dojo follows a "wrapper loop" pattern:

1. **Briefing (TUI)**: Shows lesson objectives and instructions
2. **Action (Vim)**: Launches real Vim for hands-on practice
3. **Verification**: Validates the lesson completion when user exits Vim
4. **Debrief (TUI)**: Shows results and feedback

## Directory Structure

```
vimtut/
├── dojo_app.py      # Main TUI application
├── lessons/         # Lesson configurations (JSON)
│   └── 01_the_exit.json
├── workspace/       # User workspace
│   ├── .vimrc       # Custom Vim config for tutorials
│   └── current_task.txt  # Working file
└── README.md
```

## Requirements

- Python 3.6+
- Vim (must be installed and in PATH)

## Usage

Run the tutorial:

```bash
./dojo_app.py
```

Or:

```bash
python3 dojo_app.py
```

## Controls

- **UP/DOWN arrows**: Navigate lessons
- **ENTER**: Start selected lesson
- **q**: Quit application

## Adding New Lessons

Create a new JSON file in the `lessons/` directory:

```json
{
  "id": "lesson_id",
  "title": "Lesson Title",
  "instruction_text": "Instructions for the user",
  "setup_file": "Initial file content",
  "validation_type": "exact_match|file_saved|contains",
  "target_content": "Expected result"
}
```

### Validation Types

- `file_saved`: Checks if the file was saved (for exit lesson)
- `exact_match`: File content must exactly match `target_content`
- `contains`: File must contain `target_content` substring
