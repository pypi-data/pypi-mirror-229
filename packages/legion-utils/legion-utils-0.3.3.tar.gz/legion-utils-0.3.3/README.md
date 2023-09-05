# Legion Utils

Utilities for Legion Reporters and Monitors

## Usage

TODO

## Installation & Setup

To install legion-utils with [`pip`](https://pip.pypa.io/en/stable/) execute the following:

```bash
pip install /path/to/repo/legion-utils
```

If you don't want to re-install every time there is an update, and prefer to just pull from the git repository, then use the `-e` flag.

## Development

### Standards

- Be excellent to each other
- Code coverage must be at 100% for all new code, or a good reason must be provided for why a given bit of code is not covered.
  - Example of an acceptable reason: "There is a bug in the code coverage tool and it says its missing this, but its not".
  - Example of unacceptable reason: "This is just exception handling, its too annoying to cover it".
- The code must pass the following analytics tools. Similar exceptions are allowable as in rule 2.
  - `pylint --disable=C0111,W1203,R0903 --max-line-length=100 ...`
  - `flake8 --max-line-length=100 ...`
  - `mypy --ignore-missing-imports --follow-imports=skip --strict-optional ...`
- All incoming information from users, clients, and configurations should be validated.
- All internal arguments passing should be typechecked whenever possible with `typeguard.typechecked`

### Development Setup

Using [poetry](https://python-poetry.org/) install from inside the repo directory:

```bash
poetry install
```

This will set up a virtualenv which you can always activate with either `poetry shell` or run specific commands with `poetry run`. All instructions below that are meant to be run in the virtualenv will be prefaced with `(legion-utils)$ `

#### IDE Setup

**Sublime Text 3**

```bash
curl -sSL https://gitlab.com/-/snippets/2066312/raw/master/poetry.sublime-project.py | poetry run python
```

## Testing

All testing should be done with `pytest` which is installed with the `dev` requirements.

To run all the unit tests, execute the following from the repo directory:

```bash
(legion-utils)$ pytest
```

This should produce a coverage report in `/path/to/dewey-api/htmlcov/`

While developing, you can use [`watchexec`](https://github.com/watchexec/watchexec) to monitor the file system for changes and re-run the tests:

```bash
(legion-utils)$ watchexec -r -e py,yaml pytest
```

To run a specific test file:

```bash
pytest tests/unit/test_core.py
```

To run a specific test:

```bash
pytest tests/unit/test_core.py::test_hello
```

For more information on testing, see the `pytest.ini` file as well as the [documentation](https://docs.pytest.org/en/stable/).
