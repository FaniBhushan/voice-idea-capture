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

## Agent Personas & Behaviors

The detailed behaviors and roles for specific agent personas are defined in their respective files:

*   [💻 Programmer Agent](file:///Users/fanibhushan/voice-idea-capture/.agents/programmer.md) - Rules for writing clean, testable, and maintainable code.
*   [🤝 Pair Programmer Agent](file:///Users/fanibhushan/voice-idea-capture/.agents/pair-programmer.md) - Guidelines for active collaboration and co-working styles.
*   [🔍 Reviewer Agent](file:///Users/fanibhushan/voice-idea-capture/.agents/reviewer.md) - Checklist for security, performance, error handling, and style review.
*   [🧠 Brainstormer Agent](file:///Users/fanibhushan/voice-idea-capture/.agents/brainstormer.md) - System instructions for architectural design, feature expansion, and roadmap planning.
*   [🧪 Tester Agent](file:///Users/fanibhushan/voice-idea-capture/.agents/tester.md) - Guidelines for designing, implementing, and running test coverage.

