import os, re, subprocess
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
def run(*a):
    return subprocess.run(["./vimtut.py", *a], cwd=ROOT, capture_output=True, text=True, timeout=30)

def test_executable_shebang():
    p = os.path.join(ROOT, "vimtut.py")
    assert os.access(p, os.X_OK)
    assert open(p).readline().strip() == "#!/usr/bin/env python3"

def test_help_lists_flags():
    r = run("--help")
    assert r.returncode == 0
    assert "--progress" in r.stdout and "--reset" in r.stdout

def test_invalid_option():
    assert run("--bogus").returncode != 0

def test_quick_start_link_resolves():
    readme = open(os.path.join(ROOT, "README.md")).read()
    links = re.findall(r"\]\(([^)#]+\.md)\)", readme)
    assert "QUICK_START.md" in links
    for l in links:
        assert os.path.isfile(os.path.join(ROOT, l))

def test_readme_commands_match_script():
    readme = open(os.path.join(ROOT, "README.md")).read()
    assert "./vimtut.py" in readme and "python3 vimtut.py" in readme
    assert os.path.isfile(os.path.join(ROOT, "vimtut.py"))
