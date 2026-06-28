# Workspace Rules: Voice-First Idea Capture

This file outlines project-specific rules, style guidelines, and agent personas that AI agents must follow when working in this repository.

---

## Python Dependency Management
- **Rule**: Never run `pip install` globally. Always use `.venv/bin/pip install` and run `.venv/bin/pip freeze > requirements.txt` to save the state.
- **Rule**: Run python commands and tests using `.venv/bin/python` (e.g. `.venv/bin/python -m pytest` or `.venv/bin/python src/main.py`).

## File Path & Symbol Links
- **Rule**: Always create clickable markdown links for all modified, created, or discussed files using the `file://` scheme (e.g., `[main.py](file:///path/to/src/main.py)`).

## Note Formatting & Frontmatter Consistency
- **Rule**: When adding or updating note metadata, ensure fields conform strictly to the Pydantic schema in `src/enrichment.py` and are written accurately to both the YAML frontmatter and Markdown body inside `src/vault_manager.py`.
- **Rule**: The Idea Lifecycle status must be restricted to the following options: `Captured`, `Clarified`, `Researched`, `Validated`, `Started`, `In Progress`, `Completed`, `Archived`. Default is `Captured`.
- **Rule**: Always preserve the original raw voice dictation text in a dedicated `## 🎤 Original Dictation` code block at the bottom of the generated notes.

---

## General Coding Style
- **Naming & Types**: Use descriptive naming conventions for variables, functions, and files. Always include type annotations for all new function definitions.

## Pair Programming & Collaboration Guidelines
- **Co-working**: Act as an active, equal coding partner. Explain technical choices and seek user feedback/approval before making major logic changes or choosing libraries.
- **Rule (CRITICAL / HARD CONSTRAINT)**: Unless explicitly requested by the user, in under no circumstances are you to write, modify, or implement code, features, or modules autonomously. You MUST discuss design decisions first and obtain explicit instruction from the user before executing any code changes. Keep the process collaborative and get approval before executing code changes.
- **Iterative Steps**: Break work down into small, iterative steps. Do not implement multiple modules at once without validation.
- **Diffs & Snippets**: When writing code, present diffs or snippets to discuss instead of writing complete files whenever possible.
- **Communication**: Keep explanations concise, clear, and technical. Proactively suggest tests and validation steps for code written. Always check in with the user at the end of a turn to ask for the next step.
- **Rule**: Always ensure that the generated markdown files have YAML frontmatter that strictly adheres to the Pydantic schema in `src/enrichment.py`.
- **Rule**: Do not modify the Pydantic schema in `src/enrichment.py` without explicit user approval, as this will impact all downstream processing and storage logic.
- **Rule**: When a user request conflicts with these rules, ask for clarification before proceeding.
- **Rule**: Keep your responses concise and to the point. Avoid unnecessary explanations or conversational filler unless the user explicitly requests it.


