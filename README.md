# google-java-format-hook

A pre-commit hook for automatically formatting only the modified lines of Java files using [google-java-format](https://github.com/google/google-java-format).

## Features

- Formats only the changed lines in `.java` files using `google-java-format`.
- Automatically downloads and verifies the correct version of the formatter JAR and the official diff script using Python.
- Blocks commits if formatting changes are made, requiring you to review and re-stage.

## Requirements

- `git`
- `python3`
- [pre-commit](https://pre-commit.com/)

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

- Download and verify the correct version of `google-java-format` and the diff script if not present.
- Format only the changed lines in `.java` files.
- If any files are changed, the commit will be blocked and you will be prompted to review and re-stage the files.
- To get extra logging, set `VERBOSE=1` environment variable. E.g. `VERBOSE=1 git commit ...`.

### Manual Run

To manually format only the changed lines in `.java` files, run:

```sh
git diff -U0 --no-color | python3 format.py
```

## Customization

- To change the formatter version, edit the `VERSION` variable in `format.py`.

## Testing

To run tests, ensure you have `pytest` installed, and then run:

```sh
VERBOSE=1 pytest --capture=sys
```

## License

See [LICENSE](LICENSE).
