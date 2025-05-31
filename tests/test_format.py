# Copilot generated test file for google_java_format_hook

import sys
from pathlib import Path

import pytest

print("Adding parent directory to sys.path for imports... old sys.path:", sys.path)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
print("New sys.path:", sys.path)

from google_java_format_hook import format as gjf


def test_file_md5_same(tmp_path):
    file1 = tmp_path / "A.java"
    file1.write_text("class A {}\n")
    hash1 = gjf.file_md5(file1)
    hash2 = gjf.file_md5(file1)
    assert hash1 == hash2


def test_file_md5_diff(tmp_path):
    file1 = tmp_path / "A.java"
    file2 = tmp_path / "B.java"
    file1.write_text("class A {}\n")
    file2.write_text("class B {}\n")
    hash1 = gjf.file_md5(file1)
    hash2 = gjf.file_md5(file2)
    assert hash1 != hash2


def test_download_and_check(tmp_path, monkeypatch):
    # Use a small text file from the web
    url = "https://raw.githubusercontent.com/google/google-java-format/v1.24.0/scripts/google-java-format-diff.py"
    dest = tmp_path / "test.txt"
    monkeypatch.setattr(gjf, "vprint", lambda *a, **k: None)  # silence output
    gjf.download(url, dest)
    assert dest.exists()
    assert dest.stat().st_size > 0


def test_check_and_download_assets(tmp_path, monkeypatch):
    # Patch download to just create empty files
    monkeypatch.setattr(gjf, "CACHE", tmp_path)
    monkeypatch.setattr(gjf, "VERSION_FILE", tmp_path / "VERSION.txt")
    monkeypatch.setattr(gjf, "download", lambda url, dest: dest.write_text("test"))
    monkeypatch.setattr(gjf, "vprint", lambda *a, **k: None)
    jar_path, script_path = gjf.check_and_download_assets(force_update=True)
    assert (tmp_path / gjf.JAR).exists()
    assert (tmp_path / gjf.SCRIPT).exists()
    assert (tmp_path / "VERSION.txt").exists()


def test_get_changed_java_files_empty(tmp_path, monkeypatch):
    # Patch subprocess to simulate no changed files
    monkeypatch.setattr(gjf, "subprocess", __import__("subprocess"))
    def fake_run(*a, **k):
        class R: stdout = ""; returncode = 0
        return R()
    monkeypatch.setattr(gjf.subprocess, "run", fake_run)
    assert gjf.get_changed_java_files() == []


def test_check_reformatted_by_hash(tmp_path, capsys):
    # Create a file, hash it, then change it and check detection
    file1 = tmp_path / "A.java"
    file1.write_text("class A {}\n")
    before = {str(file1): gjf.file_md5(file1)}
    file1.write_text("class A { int x; }\n")
    with pytest.raises(SystemExit) as e:
        gjf.check_reformatted_by_hash(before)
    out = capsys.readouterr().out
    assert "File reformatted" in out
    assert e.value.code == 1


def test_check_reformatted_by_hash_no_change(tmp_path, capsys):
    file1 = tmp_path / "A.java"
    file1.write_text("class A {}\n")
    before = {str(file1): gjf.file_md5(file1)}
    with pytest.raises(SystemExit) as e:
        gjf.check_reformatted_by_hash(before)
    out = capsys.readouterr().out
    assert "No files needed reformatting." in out
    assert e.value.code == 0
