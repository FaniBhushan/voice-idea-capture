---
name: voice-idea-pipeline
description: |
  Guides the agent on how to maintain, test, run, and extend the voice-first idea
  capture and Obsidian ingestion pipeline in this repository.
  Activate this skill when:
  1. Modifying the ingestion pipeline CLI, configuration, or watcher.
  2. Editing the LLM enrichment schema (e.g. adding new frontmatter fields).
  3. Updating the Obsidian vault manager or markdown template.
  4. Debugging or running pipeline tests.
---

# Voice-First Idea Ingestion Pipeline Skill

Use this skill to understand the pipeline architecture, schemas, and verification steps when developing this codebase.

## Repository Layout
- `src/config.py`: Core configuration, path management, and environment variables (.env).
- `src/enrichment.py`: LLM structured output parsing using Google GenAI SDK and Pydantic.
- `src/vault_manager.py`: Handles existing vault index scanning, title sanitization, and Markdown formatting.
- `src/watcher.py`: Hot-folder monitoring using `watchdog` to automatically run imports.
- `src/main.py`: CLI console entry point (`run`, `watch`, `status`).
- `shortcuts/export_ideas.applescript`: macOS Apple Notes exporter template.
- `tests/test_pipeline.py`: Pytest suite for sanitization, formatting, and mock ingestion testing.

## Dependency Management
This project uses virtual environment (`.venv`) and a standard `requirements.txt` file.
Always run pip installs and commands using:
```bash
.venv/bin/pip install <package>
.venv/bin/python <script>
```

## LLM Ingestion Schema
The enrichment engine is powered by the `google-genai` SDK and expects the `NoteEnrichment` Pydantic schema in `src/enrichment.py`.
If you need to add, modify, or delete metadata fields:
1. Update `NoteEnrichment` in `src/enrichment.py`.
2. Update the prompt inside the `enrich_note` function in `src/enrichment.py`.
3. Update `format_markdown_note` in `src/vault_manager.py` to write the new fields into the frontmatter or markdown body.
4. Update unit tests in `tests/test_pipeline.py`.

## CLI Usage Reference
- **Run batch ingestion:** `python3 src/main.py run` (processes pending files in `input/` and archives them in `processed/`).
- **Start directory watcher:** `python3 src/main.py watch` (runs watchdog thread over `input/`).
- **Show vault dashboard:** `python3 src/main.py status` (displays statistics on categories, status, and tags).

## Testing Guidelines
Run the verification suite using:
```bash
.venv/bin/python -m pytest tests/test_pipeline.py
```
Ensure all mock data matches the Pydantic schema.
