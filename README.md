# Voice-First Idea Capture & Obsidian Ingestion Pipeline

A collaborative project to build a local-first automation pipeline that ingests raw voice-dictation transcripts, enriches them with LLM metadata, and stores them in Obsidian.

## 📋 Table of Contents
- [🗺️ Project Scope](#️-project-scope)
- [🔄 Ingestion Pipeline Flow](#-ingestion-pipeline-flow)
  - [High-Level Conceptual Flow](#high-level-conceptual-flow)
  - [Detailed Component Flow](#detailed-component-flow)
- [⚙️ Setup & Configuration](#️-setup--configuration)
- [🚀 CLI Commands](#-cli-commands)
  - [Command Line Options](#️-command-line-options)
  - [macOS Integration & Automation](#-macos-integration--automation)
- [🔮 Actionable Roadmap & Improvement Ideas](#-actionable-roadmap--improvement-ideas)

---

## 🗺️ Project Scope
- **Ingestion Pipeline**: Watches or scans the hidden input directory `~/.voice-idea-capture/input` for text files (`.txt` or `.md`).
- **LLM Enrichment**: Leverages the Gemini API to analyze the raw notes, generate structured YAML metadata (adhering to a Pydantic schema for categorization, status, effort, next actions, etc.), and summarize the core ideas.
- **Vault Management**: Formats the enriched data as Markdown, checks for existing title conflicts, and writes the notes to your Obsidian vault.
- **Archiving**: Moves processed raw inputs to `~/.voice-idea-capture/processed/`.

## 🔄 Ingestion Pipeline Flow

### High-Level Conceptual Flow
```mermaid
graph LR
    Input[(~/.voice-idea-capture/input/)] -->|Detects change| Watcher[Watcher]
    Watcher -->|Read transcript| Enricher[Enricher]
    Enricher -->|Structured metadata| VaultMgr[Vault Manager]
    VaultMgr -->|Check & write note| Vault[(Obsidian Vault)]
    Watcher -->|Move raw file| Archive[(~/.voice-idea-capture/processed/)]
```

### Detailed Component Flow
```mermaid
graph TD
    A[🎤 Voice Dictation] -->|Save Text/MD| B(~/.voice-idea-capture/input/)
    B -->|File Created / watchdog| C[watcher.py]
    C -->|Trigger Processing| D[main.py / CLI]
    D -->|Read File Content| E[vault_manager.py]
    E -->|Check Existing Note Titles| F{Title Conflict?}
    F -->|No / Resolve| G[enrichment.py]
    G -->|Call Gemini API with Schema| H[Gemini LLM]
    H -->|Return Structured JSON| G
    G -->|Return Enriched Data| D
    D -->|Generate Markdown & Frontmatter| E
    E -->|Write File| I[Obsidian Vault]
    D -->|Move Raw Input File| J[~/.voice-idea-capture/processed/]
```



## ⚙️ Setup & Configuration
1. Initialize virtual environment and install the package:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
2. Copy environment settings and specify API credentials:
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY inside the .env file
   ```

## 🚀 CLI Commands
The project is packaged with the custom CLI tool `idea-capture`. You can run these commands from the project root (using the virtualenv path `.venv/bin/idea-capture`) or globally if you activate the virtual environment (`source .venv/bin/activate`):

- **Sync and Process Notes**:
  ```bash
  .venv/bin/idea-capture run
  ```
  *(Automatically pulls `@idea` notes from Apple Notes, enriches them with Gemini, and saves them to Obsidian in one step).*

- **Watch directory in real-time**:
  ```bash
  .venv/bin/idea-capture watch
  ```

- **Check current pipeline status**:
  ```bash
  .venv/bin/idea-capture status
  ```

### ⚙️ Command Line Options
You can override any environment configuration paths directly using CLI flags:
* `--input-dir` or `-i`: Override the input folder path.
* `--processed-dir` or `-p`: Override the processed archive folder path.
* `--vault-path` or `-v`: Override the destination Obsidian vault path.

*Example (run status check on a custom vault)*:
```bash
.venv/bin/idea-capture --vault-path ~/Documents/PersonalVault status
```

### 🍎 macOS Integration & Automation
* **Export Notes Manually**:
  If you want to manually run the export from Apple Notes without triggering the ingestion pipeline, you can run the AppleScript directly:
  ```bash
  osascript shortcuts/export_ideas.applescript
  ```

* **Global Access**:
  To run `idea-capture` globally from anywhere on your Mac, choose one of these options:

  **Option 1: Using pipx (Recommended)**
  `pipx` installs python CLI utilities in isolated environments and exposes them globally. Run this from the project root directory:
  ```bash
  # Install pipx (if you don't have it)
  brew install pipx
  pipx ensurepath
  
  # Install the package globally in editable mode
  pipx install --editable .
  ```
  *(Now the `idea-capture` command is available globally in any folder!)*

  **Option 2: Creating a Symlink**
  Symlink the virtual environment executable into a folder in your `$PATH` (like `/usr/local/bin`):
  ```bash
  ln -s /path/to/voice-idea-capture/.venv/bin/idea-capture /usr/local/bin/idea-capture
  ```

  **Option 3: Shell Alias**
  Add an alias to your shell config (e.g., `~/.zshrc`):
  ```bash
  echo 'alias idea-capture="/path/to/voice-idea-capture/.venv/bin/idea-capture"' >> ~/.zshrc
  source ~/.zshrc
  ```


## 🔮 Actionable Roadmap & Improvement Ideas

To transition the prototype into a robust product, future enhancements are structured into three development phases:

### Phase 1: Obsidian Prioritization & Visualization
Tools to help you organize and prioritize ideas within Obsidian today.

| Feature / Improvement | Actionable Steps | Impact | Complexity |
| :--- | :--- | :---: | :---: |
| **Kanban Board Integration** | 1. Set up a Kanban card layout based on note frontmatter status.<br>2. Let users drag notes between status columns. | **High** | **Easy** |
| **Dataview Priority Queries** | 1. Add SQL-like queries inside notes to filter by `value` and `effort`.<br>2. Sort notes by priority (e.g., High Value + Low Effort first). | **High** | **Easy** |
| **Canvas / Mind Map Maker** | 1. Write script to parse tags and next actions.<br>2. Generate an Obsidian `.canvas` file showing visual linkages between projects. | **Medium** | **Hard** |

---

### Phase 2: Core Ingestion & OS Integration
Focuses on making dictation capture faster and support more formats.

| Feature / Improvement | Actionable Steps | Impact | Complexity |
| :--- | :--- | :---: | :---: |
| **Direct Audio Transcription** | 1. Update CLI to accept audio extensions (`.mp3`, `.m4a`, `.wav`).<br>2. Pass the audio stream directly to Gemini's multimodal API.<br>3. Extract and save the transcript before enrichment. | **High** | **Easy** |
| **Siri Shortcuts Integration** | 1. Create a Siri Shortcut to record voice memos on Apple Watch / iPhone.<br>2. Auto-tag with `@idea` and save to Apple Notes.<br>3. Syncs via iCloud to the Mac notes directory. | **High** | **Easy** |
| **Interactive Conflict CLI** | 1. Detect title collisions during the `run` command.<br>2. Prompt the user: `[O]verwrite / [M]erge / [R]ename / [S]uffix`. | **Medium** | **Medium** |

---

### Phase 3: Packaged Local Web Dashboard
A fully self-contained Web UI to search, prioritize, and visualize notes.

| Feature / Improvement | Actionable Steps | Impact | Complexity |
| :--- | :--- | :---: | :---: |
| **Local FastAPI Server** | 1. Create local API endpoints (`/api/notes`) in Python to parse markdown files.<br>2. Serve compiled React frontend assets from FastAPI. | **High** | **Medium** |
| **Fuzzy Search & Filters** | 1. Integrate `Fuse.js` in the frontend for instant search.<br>2. Add custom filters for category, status, and tag. | **High** | **Medium** |
| **Effort vs. Value Matrix** | 1. Build an interactive scatter plot grid (Effort vs. Value).<br>2. Highlight *Quick Wins* (High Value, Low Effort) in green. | **High** | **Medium** |
| **Single-File Packaging** | 1. Use `PyInstaller` to compile Python, FastAPI, and React into a single binary.<br>2. Add `idea-capture dashboard` CLI launcher command. | **Medium** | **Hard** |
