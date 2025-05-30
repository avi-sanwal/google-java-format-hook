# google-java-format-hook

A pre-commit hook for automatically formatting only the modified lines of staged Java files using [google-java-format](https://github.com/google/google-java-format).

## Features

- Formats only the changed lines in staged `.java` files using `google-java-format`.
- Automatically downloads and verifies the correct version of the formatter JAR and the official diff script using Python.
- Ensures files are not corrupt or outdated by checking SHA256 hashes.
- Blocks commits if formatting changes are made, requiring you to review and re-stage.

## Requirements

- `git`
- `python3`

## Installation

1. Install [pre-commit](https://pre-commit.com/):

   ```sh
   pip install pre-commit
   ```

2. Add this repo as a hook in your project's `.pre-commit-config.yaml`:

   ```yaml
   - repo: https://github.com/avi-sanwal/google-java-format-hook.git
     rev: main # or the latest release/tag
     hooks:
       - id: google-java-format-hook
   ```

3. Install the pre-commit hook:
   ```sh
   pre-commit install
   ```

## Usage

On commit, the hook will:

- Download and verify the correct version of `google-java-format` and the diff script if not present or if corrupt.
- Format only the changed lines in staged `.java` files.
- If any files are changed, the commit will be blocked and you will be prompted to review and re-stage the files.

You can also run the hook manually:

```sh
git diff -U0 --no-color | python3 format.py
```

## Customization

- To change the formatter version, edit the `VERSION` variable in `format.py`.

## License

See [LICENSE](LICENSE).
