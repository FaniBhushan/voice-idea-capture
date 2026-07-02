import sys
import shutil
import re
from pathlib import Path
from src.config import INPUT_DIR, PROCESSED_DIR, OBSIDIAN_VAULT_PATH
from src.enrichment import enrich_note
from src.vault_manager import VaultManager
from src.watcher import watch_input_directory

def parse_frontmatter(content: str) -> dict:
    """Helper to parse status, category, and tags from YAML frontmatter without PyYAML."""
    data = {}
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if match:
        frontmatter_text = match.group(1)
        current_key = None
        for line in frontmatter_text.splitlines():
            line_stripped = line.strip()
            if not line_stripped:
                continue
            if line_stripped.startswith("-"):
                if current_key:
                    val = line_stripped[1:].strip().strip('"').strip("'")
                    if current_key not in data or not isinstance(data[current_key], list):
                        data[current_key] = []
                    data[current_key].append(val)
            elif ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if val == "":
                    data[key] = []
                else:
                    data[key] = val
                current_key = key
    return data

def process_file(file_path: Path, vault_manager: VaultManager):
    """Orchestrates the ingestion, enrichment, saving, and archiving of a single file."""
    print(f"\nProcessing: {file_path.name}")
    try:
        raw_content = file_path.read_text(encoding="utf-8")
        if not raw_content.strip():
            print(f"Skipping empty file: {file_path.name}")
            return

        existing_titles = vault_manager.get_existing_note_titles()
        print("Calling LLM for enrichment...")
        enrichment = enrich_note(raw_content, existing_titles)
        
        print("Saving to Obsidian Vault...")
        saved_path = vault_manager.save_note_to_vault(enrichment, raw_content)
        print(f"Saved to: {saved_path}")

        # Ensure processed directory exists
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        # Move raw file to archive
        shutil.move(str(file_path), str(PROCESSED_DIR / file_path.name))
        print(f"Archived original file to: {PROCESSED_DIR / file_path.name}")
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")

def run_command():
    """Processes all files currently in the input directory."""
    vault_manager = VaultManager(OBSIDIAN_VAULT_PATH)
    input_files = [f for f in INPUT_DIR.glob("*") if f.is_file() and f.suffix in [".txt", ".md"]]
    
    if not input_files:
        print("No pending voice notes in the input folder.")
        return

    print(f"Found {len(input_files)} file(s) to process.")
    for file_path in input_files:
        process_file(file_path, vault_manager)

def watch_command():
    """Starts the watcher to process new files automatically as they arrive."""
    vault_manager = VaultManager(OBSIDIAN_VAULT_PATH)
    
    def file_change_callback(file_path_str: str):
        file_path = Path(file_path_str)
        if file_path.exists() and file_path.is_file():
            process_file(file_path, vault_manager)

    print(f"Starting watcher on folder: {INPUT_DIR}")
    print("Press Ctrl+C to exit.")
    watch_input_directory(file_change_callback, INPUT_DIR)

def status_command():
    """Scans the vault and shows statistics of the notes."""
    vault_manager = VaultManager(OBSIDIAN_VAULT_PATH)
    notes = list(OBSIDIAN_VAULT_PATH.glob("*.md"))
    
    if not notes:
        print("\nNo notes found in the Obsidian Vault.")
        return
        
    status_counts = {}
    category_counts = {}
    tag_counts = {}

    for note_path in notes:
        content = note_path.read_text(encoding="utf-8")
        metadata = parse_frontmatter(content)
        
        status = metadata.get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        
        category = metadata.get("category", "Unknown")
        category_counts[category] = category_counts.get(category, 0) + 1
        
        tags = metadata.get("tags", [])
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print("\n==================================")
    print("      Obsidian Vault Status       ")
    print("==================================")
    print(f"Total Notes: {len(notes)}")
    
    print("\nNotes by Status:")
    for status, count in sorted(status_counts.items()):
        print(f"  - {status}: {count}")
        
    print("\nNotes by Category:")
    for category, count in sorted(category_counts.items()):
        print(f"  - {category}: {count}")
        
    print("\nTop Tags:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - #{tag}: {count}")
    print("==================================\n")

def main():
    if len(sys.argv) < 2:
        print("Voice Idea Capture CLI")
        print("Usage: python3 src/main.py [run|watch|status]")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    
    if command == "run":
        run_command()
    elif command == "watch":
        watch_command()
    elif command == "status":
        status_command()
    else:
        print(f"Unknown command: '{command}'")
        print("Usage: python3 src/main.py [run|watch|status]")
        sys.exit(1)

if __name__ == "__main__":
    main()

