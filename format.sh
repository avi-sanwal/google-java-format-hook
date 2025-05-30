#!/usr/bin/env sh

VERSION="1.24.0"
JAR="google-java-format-${VERSION}-all-deps.jar"
JAR_SHA256_FILE="google-java-format-${VERSION}-all-deps.jar.sha256"
SCRIPT="google-java-format-diff.py"
SCRIPT_URL="https://raw.githubusercontent.com/google/google-java-format/v${VERSION}/scripts/google-java-format-diff.py"
JAR_URL="https://github.com/google/google-java-format/releases/download/v${VERSION}/${JAR}"
JAR_SHA256_URL="https://github.com/google/google-java-format/releases/download/v${VERSION}/${JAR_SHA256_FILE}"

mkdir -p .cache
cd .cache

# Download and verify JAR
need_jar_download=0
if [ ! -f "$JAR" ] || [ ! -f "$JAR_SHA256_FILE" ]; then
    need_jar_download=1
else
    # Verify hash
    sha256sum -c "$JAR_SHA256_FILE" 2>/dev/null || need_jar_download=1
fi
if [ $need_jar_download -eq 1 ]; then
    echo "Downloading $JAR and verifying hash..."
    curl -LJO "$JAR_URL"
    curl -LJO "$JAR_SHA256_URL"
    if ! sha256sum -c "$JAR_SHA256_FILE"; then
        echo "JAR hash mismatch after download. Aborting." >&2
        exit 2
    fi
    chmod 755 "$JAR"
fi

# Download and verify script
SCRIPT_HASH_EXPECTED="$(curl -sL "$SCRIPT_URL" | shasum -a 256 | awk '{print $1}')"
need_script_download=0
if [ ! -f "$SCRIPT" ]; then
    need_script_download=1
else
    SCRIPT_HASH_LOCAL="$(shasum -a 256 "$SCRIPT" | awk '{print $1}')"
    [ "$SCRIPT_HASH_LOCAL" != "$SCRIPT_HASH_EXPECTED" ] && need_script_download=1
fi
if [ $need_script_download -eq 1 ]; then
    echo "Downloading $SCRIPT..."
    curl -LJO "$SCRIPT_URL"
    SCRIPT_HASH_LOCAL="$(shasum -a 256 "$SCRIPT" | awk '{print $1}')"
    if [ "$SCRIPT_HASH_LOCAL" != "$SCRIPT_HASH_EXPECTED" ]; then
        echo "Script hash mismatch after download. Aborting." >&2
        exit 2
    fi
    chmod 755 "$SCRIPT"
fi
cd ..

# Get staged diff for .java files only
STAGED_DIFF=$(git diff --cached --diff-filter=ACM -U0 --no-color -- '*.java')

if [ -z "$STAGED_DIFF" ]; then
  exit 0
fi

echo "$STAGED_DIFF" | python3 .cache/google-java-format-diff.py -i -p1 --google-java-format-jar .cache/google-java-format-${VERSION}-all-deps.jar

# Check if any .java files were modified by the formatter
CHANGED_FILES=$(git diff --name-only -- '*.java')
if [ -n "$CHANGED_FILES" ]; then
  echo "Some files were reformatted. Please review and re-stage."
  exit 1
fi

exit 0
