#!/usr/bin/env python3
import os
import sys
import subprocess
import hashlib
import urllib.request
from pathlib import Path

VERSION = "1.24.0"
CACHE = Path(".cache")
JAR = f"google-java-format-{VERSION}-all-deps.jar"
JAR_SHA256 = f"google-java-format-{VERSION}-all-deps.jar.sha256"
SCRIPT = "google-java-format-diff.py"
SCRIPT_URL = f"https://raw.githubusercontent.com/google/google-java-format/v{VERSION}/scripts/google-java-format-diff.py"
JAR_URL = f"https://github.com/google/google-java-format/releases/download/v{VERSION}/{JAR}"
JAR_SHA256_URL = f"https://github.com/google/google-java-format/releases/download/v{VERSION}/{JAR_SHA256}"

CACHE.mkdir(exist_ok=True)

# Download helper
def download(url, dest):
    with urllib.request.urlopen(url) as r, open(dest, 'wb') as f:
        f.write(r.read())

def sha256sum(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def verify_file(path, sha256_file):
    with open(sha256_file) as f:
        expected = f.read().split()[0]
    actual = sha256sum(path)
    return actual == expected

# JAR download and verify
jar_path = CACHE / JAR
jar_sha_path = CACHE / JAR_SHA256
need_jar = not (jar_path.exists() and jar_sha_path.exists() and verify_file(jar_path, jar_sha_path))
if need_jar:
    print(f"Downloading {JAR} and verifying hash...")
    download(JAR_URL, jar_path)
    download(JAR_SHA256_URL, jar_sha_path)
    if not verify_file(jar_path, jar_sha_path):
        print("JAR hash mismatch after download. Aborting.", file=sys.stderr)
        sys.exit(2)
    jar_path.chmod(0o755)

# Script download and verify
script_path = CACHE / SCRIPT
with urllib.request.urlopen(SCRIPT_URL) as r:
    script_content = r.read()
    script_hash_expected = hashlib.sha256(script_content).hexdigest()
need_script = not (script_path.exists() and hashlib.sha256(script_path.read_bytes()).hexdigest() == script_hash_expected)
if need_script:
    print(f"Downloading {SCRIPT}...")
    with open(script_path, 'wb') as f:
        f.write(script_content)
    if hashlib.sha256(script_path.read_bytes()).hexdigest() != script_hash_expected:
        print("Script hash mismatch after download. Aborting.", file=sys.stderr)
        sys.exit(2)
    script_path.chmod(0o755)

# Get staged diff for .java files only
git_diff = subprocess.run([
    "git", "diff", "--cached", "--diff-filter=ACM", "-U0", "--no-color", "--", "*.java"
], capture_output=True, text=True)
STAGED_DIFF = git_diff.stdout
if not STAGED_DIFF.strip():
    sys.exit(0)

# Run formatter
diff_proc = subprocess.run([
    sys.executable, str(script_path), "-i", "-p1", "--google-java-format-jar", str(jar_path)
], input=STAGED_DIFF, text=True)

# Check if any .java files were modified by the formatter
changed = subprocess.run(["git", "diff", "--name-only", "--", "*.java"], capture_output=True, text=True)
if changed.stdout.strip():
    print("Some files were reformatted. Please review and re-stage.")
    sys.exit(1)

sys.exit(0)
