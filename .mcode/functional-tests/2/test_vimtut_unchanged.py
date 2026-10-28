import subprocess, sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def test_help_unchanged():
    p = subprocess.run([sys.executable, "vimtut.py", "--help"], cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert p.returncode == 0
    assert "usage" in p.stdout.lower()
