import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def vt(tmp_path):
    # Work on an isolated copy so workspace/progress files are not touched.
    dst = tmp_path / "vimtut"
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".mcode", "__pycache__", "progress.json"))
    sys.path.insert(0, str(dst))
    sys.modules.pop("vimtut", None)
    import vimtut
    try:
        yield vimtut.Vimtut()
    finally:
        sys.path.remove(str(dst))
        sys.modules.pop("vimtut", None)


def test_lessons_loaded_and_ordered(vt):
    assert len(vt.basic_lessons) > 0
    assert len(vt.lessons) == len(vt.basic_lessons) + len(vt.advanced_lessons)
    ids = [l["id"] for l in vt.basic_lessons]
    assert len(ids) == len(set(ids))


def test_get_lesson_by_id(vt):
    assert vt.get_lesson_by_id("append_mode")["id"] == "append_mode"
    assert vt.get_lesson_by_id("does_not_exist") is None


def test_progress_roundtrip(vt):
    vt.completed_lessons = {"append_mode"}
    vt.welcome_seen = True
    vt.save_progress()
    done, seen = vt.load_progress()
    assert done == {"append_mode"} and seen is True


def test_load_progress_corrupt_file(vt):
    vt.progress_file.write_text("{corrupt")
    assert vt.load_progress() == (set(), False)


def test_setup_and_validate_exact_match(vt):
    lesson = vt.get_lesson_by_id("append_mode")
    vt.setup_lesson(lesson)
    assert vt.current_lesson_file.read_text() == lesson["setup_file"]
    ok, _ = vt.validate_lesson(lesson)
    assert ok is False
    vt.current_lesson_file.write_text(lesson["target_content"])
    ok, msg = vt.validate_lesson(lesson)
    assert ok is True, msg


@pytest.mark.parametrize("key,buf,pend,exp", [
    (ord("G"), "", False, (True, "", False, 4)),
    (ord("g"), "", False, (True, "", True, None)),
    (ord("g"), "", True, (True, "", False, 0)),
    (ord("3"), "", False, (True, "3", False, None)),
    (ord("0"), "", False, (True, "", False, None)),
    (ord("G"), "99", False, (True, "", False, 4)),
    (ord("x"), "", False, (False, "", False, None)),
])
def test_handle_goto_key(vt, key, buf, pend, exp):
    assert vt.handle_goto_key(key, buf, pend, 4) == exp
