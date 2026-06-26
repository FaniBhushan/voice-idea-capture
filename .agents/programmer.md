# 💻 Programmer Agent

Rules for writing clean, testable, and maintainable code in this repository.

## Python Dependency Management
- **Rule**: Never run `pip install` globally. Always use `.venv/bin/pip install` and run `.venv/bin/pip freeze > requirements.txt` to save the state.
- **Rule**: Run python commands and tests using `.venv/bin/python` (e.g. `.venv/bin/python -m pytest` or `.venv/bin/python src/main.py`).

## Code style & conventions
- Use descriptive naming conventions for variables, functions, and files.
- Always include type annotations for all new function definitions.
- Always create clickable markdown links for all modified, created, or discussed files using the `file://` scheme.

