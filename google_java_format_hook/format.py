#!/usr/bin/env python3
import hashlib
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

VERSION = "1.24.0"
CACHE = Path(".cache")
JAR = f"google-java-format-{VERSION}-all-deps.jar"
SCRIPT = "google-java-format-diff.py"
SCRIPT_URL = f"https://raw.githubusercontent.com/google/google-java-format/v{VERSION}/scripts/google-java-format-diff.py"
JAR_URL = f"https://github.com/google/google-java-format/releases/download/v{VERSION}/{JAR}"
VERSION_FILE = CACHE / "VERSION.txt"

JAVA_GLOB = "*.java"
DIFF_FILTER = "--diff-filter=ACM"


def is_verbose():
    return os.environ.get("VERBOSE", "0") == "1" or "-v" in sys.argv or "--verbose" in sys.argv


def vprint(*args, **kwargs):
    if is_verbose():
        print(*args, **kwargs)


def download(url, dest):
    vprint(f"Downloading {url} to {dest}...")
    with urllib.request.urlopen(url) as r, open(dest, 'wb') as f:
        f.write(r.read())


def check_and_download_assets(force_update: bool):
    prev_version = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else None
    version_changed = prev_version != VERSION
    force_update = force_update or version_changed

    jar_path = CACHE / JAR
    if force_update or not jar_path.exists():
        download(JAR_URL, jar_path)
        jar_path.chmod(0o755)

    script_path = CACHE / SCRIPT
    if force_update or not script_path.exists():
        download(SCRIPT_URL, script_path)
        script_path.chmod(0o755)

    VERSION_FILE.write_text(VERSION)
    return jar_path, script_path


def get_staged_and_unstaged_diff():
    vprint("Getting staged and unstaged diff for .java files...")
    # Get staged diff
    staged = subprocess.run([
        "git", "diff", "--cached", DIFF_FILTER, "-U0", "--no-color", "--", JAVA_GLOB
    ], capture_output=True, text=True).stdout
    # Get unstaged diff
    unstaged = subprocess.run([
        "git", "diff", DIFF_FILTER, "-U0", "--no-color", "--", JAVA_GLOB
    ], capture_output=True, text=True).stdout
    # Combine, but avoid duplicate diffs for the same file/line
    combined = staged + unstaged
    return combined


def run_formatter(script_path, jar_path, staged_diff):
    vprint(f"Running formatter: {script_path} on diff with jar {jar_path}")
    formatter_cmd = [
        sys.executable, str(script_path), "-i", "-p1", "--google-java-format-jar", str(jar_path)
    ]
    if is_verbose():
        formatter_cmd.insert(1, "-v")
    vprint("Running command:", " ".join(formatter_cmd))
    subprocess.run(formatter_cmd, input=staged_diff, text=True)


def get_changed_java_files():
    # Get all staged and unstaged .java files with changes
    result = subprocess.run([
        "git", "status", "--porcelain", "--", JAVA_GLOB
    ], capture_output=True, text=True)
    files = set()
    for line in result.stdout.splitlines():
        # line format: XY filename
        parts = line.strip().split()
        if len(parts) == 2:
            files.add(parts[1])
    return list(files)


def file_md5(path):
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def check_reformatted_by_hash(files_before):
    changed = False
    for path, old_hash in files_before.items():
        try:
            new_hash = file_md5(path)
            if new_hash != old_hash:
                print(f"File reformatted: {path}")
                changed = True
        except Exception as e:
            vprint(f"Warning: Could not check file {path}: {e}")
    if changed:
        print("Some files were reformatted. Please review and re-stage.")
        sys.exit(1)
    vprint("No files needed reformatting.")
    sys.exit(0)


def main():
    CACHE.mkdir(exist_ok=True)
    force_update = os.environ.get("FORCE_UPDATE", "0") == "1"
    jar_path, script_path = check_and_download_assets(force_update)
    staged_diff = get_staged_and_unstaged_diff()
    if not staged_diff.strip():
        vprint("No staged or unstaged .java changes found.")
        sys.exit(0)
    # Collect all changed .java files and their hash before formatting
    changed_files = get_changed_java_files()
    files_before = {}
    for path in changed_files:
        try:
            files_before[path] = file_md5(path)
        except Exception as e:
            vprint(f"Warning: Could not hash file {path}: {e}")
    run_formatter(script_path, jar_path, staged_diff)
    check_reformatted_by_hash(files_before)


if __name__ == "__main__":
    main()
