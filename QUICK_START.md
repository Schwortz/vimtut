# Quick Start Guide

## Installation

```bash
git clone <repo-url>
cd vimtut
chmod +x vimtut.py
```

## Requirements

- Python 3.6+
- Vim (installed and in PATH)

## Launch

```bash
./vimtut.py
```

## Learning Path

### Phase 1: Basic Lessons (1-20)
Start here! Learn Vim fundamentals:
- Navigation, editing, visual mode
- Copy/paste, undo/redo
- Search, replace, line operations

**Time:** ~2-3 hours to complete all basics

### Phase 2: Advanced Lessons (21-27)
Unlock after completing basics:
- Macros, marks, registers
- Multiple files, split windows
- Find & replace, code folding

**Time:** ~1-2 hours to master advanced features

## Controls

### Main Menu
- **j/k** or **↑/↓** - Navigate lessons
- **ENTER** - Start lesson
- **a** - Switch to Advanced lessons (when unlocked)
- **b** - Return to Basic lessons
- **q** - Quit

### Inside Vim
- **Ctrl+j** - View instructions pane (bottom)
- **Ctrl+k** - Return to edit pane (top)
- **:wq** - Save and complete lesson
- **ESC** then **:q!** then **:qall!** - Quit without saving

### After Lesson
- **ENTER** - Continue or retry
- **ESC** or **q** - Return to menu

## Testing/Debugging

### Skip to Specific Lesson
```bash
# Complete first 10 lessons
./vimtut.py --progress 10

# Complete all basics (unlock advanced)
./vimtut.py --progress 20

# Complete everything
./vimtut.py --progress 27
```

### Reset Progress
```bash
./vimtut.py --reset
```

### Preview Celebrations
```bash
python3 test_celebration.py
```

## Tips for Success

1. **Read the instructions** in the bottom pane
2. **Don't rush** - practice each command
3. **Use Ctrl+j/k** to review instructions anytime
4. **Press ESC** before :wq to ensure normal mode
5. **Try commands** even if they're optional
6. **Review basics** before tackling advanced

## Common Issues

### "File exists" error
- You're in the wrong mode - press ESC first
- Then try :wq again

### Can't see instructions
- Press Ctrl+j to move to instructions pane
- Press Ctrl+k to return to edit pane

### Validation fails
- Check the debrief screen for what's different
- Press ENTER to retry
- Press ESC or 'q' to return to menu

### Both panes close unexpectedly
- This is correct! The app uses custom quit commands
- Both panes should close together with :wq

## Progress Tracking

Your progress is saved automatically in `progress.json`:
- Completed lessons marked with [x]
- Progress percentage shown in menu
- Resume anytime from where you left off

## Getting Help

- Read lesson instructions carefully (Ctrl+j)
- Review README.md for detailed docs
- Check ADVANCED_LESSONS.md for advanced topics
- Look at DEBUG_FLAGS.md for testing options

## Your First Session

1. Launch: `./vimtut.py`
2. Press ENTER on "The Exit"
3. Follow instructions in bottom pane
4. Type `:wq` and press ENTER
5. See success screen!
6. Continue to lesson 2...

Complete all 20 basics to unlock advanced lessons!

## Motivation

Track your journey:
- **0-5 lessons:** Beginner
- **6-10 lessons:** Getting comfortable
- **11-15 lessons:** Intermediate
- **16-20 lessons:** Basic mastery → Advanced unlocked! 🎓
- **21-25 lessons:** Power user
- **26-27 lessons:** Almost there...
- **27/27 lessons:** VIM MASTER! 🎉⚡

Good luck on your journey to Vim mastery!
