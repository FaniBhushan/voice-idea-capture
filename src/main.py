import sys
import shutil
import re
import argparse
import subprocess
from pathlib import Path
from src.config import INPUT_DIR, PROCESSED_DIR, OBSIDIAN_VAULT_PATH, PROJECT_ROOT
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

def process_file(file_path: Path, vault_manager: VaultManager, processed_dir: Path = PROCESSED_DIR):
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
        processed_dir.mkdir(parents=True, exist_ok=True)
        # Move raw file to archive
        shutil.move(str(file_path), str(processed_dir / file_path.name))
        print(f"Archived original file to: {processed_dir / file_path.name}")
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")

def run_command(input_dir: Path = INPUT_DIR, processed_dir: Path = PROCESSED_DIR, vault_path: Path = OBSIDIAN_VAULT_PATH):
    """Processes all files currently in the input directory, after syncing from Apple Notes."""
    # Trigger Apple Notes Sync first
    applescript_path = PROJECT_ROOT / "shortcuts/export_ideas.applescript"
    print(f"Syncing notes from Apple Notes...")
    try:
        result = subprocess.run(
            ["osascript", str(applescript_path)],
            capture_output=True,
            text=True,
            check=True
        )
        export_count = int(result.stdout.strip() or 0)
        if export_count > 0:
            print(f"Exported {export_count} new note(s) from Apple Notes.")
    except Exception as e:
        print(f"Warning: Apple Notes sync failed: {e}")

    vault_manager = VaultManager(vault_path)
    input_files = [f for f in input_dir.glob("*") if f.is_file() and f.suffix in [".txt", ".md"]]
    
    if not input_files:
        print("No pending voice notes in the input folder.")
        return

    print(f"Found {len(input_files)} file(s) to process.")
    for file_path in input_files:
        process_file(file_path, vault_manager, processed_dir)

def watch_command(input_dir: Path = INPUT_DIR, processed_dir: Path = PROCESSED_DIR, vault_path: Path = OBSIDIAN_VAULT_PATH):
    """Starts the watcher to process new files automatically as they arrive."""
    vault_manager = VaultManager(vault_path)
    
    def file_change_callback(file_path_str: str):
        file_path = Path(file_path_str)
        if file_path.exists() and file_path.is_file():
            process_file(file_path, vault_manager, processed_dir)

    print(f"Starting watcher on folder: {input_dir}")
    print("Press Ctrl+C to exit.")
    watch_input_directory(file_change_callback, input_dir)

def status_command(vault_path: Path = OBSIDIAN_VAULT_PATH):
    """Scans the vault and shows statistics of the notes."""
    vault_manager = VaultManager(vault_path)
    notes = list(vault_path.glob("*.md"))
    
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
    parser = argparse.ArgumentParser(description="Voice Idea Capture CLI")
    
    # Optional parameters to override configuration paths
    parser.add_argument(
        "--input-dir", "-i",
        type=str,
        default=str(INPUT_DIR),
        help=f"Directory where raw transcripts are placed (default: {INPUT_DIR})"
    )
    parser.add_argument(
        "--processed-dir", "-p",
        type=str,
        default=str(PROCESSED_DIR),
        help=f"Directory where processed transcripts are archived (default: {PROCESSED_DIR})"
    )
    parser.add_argument(
        "--vault-path", "-v",
        type=str,
        default=str(OBSIDIAN_VAULT_PATH),
        help=f"Path to the Obsidian vault directory (default: {OBSIDIAN_VAULT_PATH})"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to run")
    subparsers.add_parser("run", help="Process pending transcripts once")
    subparsers.add_parser("watch", help="Watch directory in real-time")
    subparsers.add_parser("status", help="Check current vault dashboard status")
    
    args = parser.parse_args()
    
    # Resolve paths (expand ~)
    input_path = Path(args.input_dir).expanduser()
    processed_path = Path(args.processed_dir).expanduser()
    vault_path = Path(args.vault_path).expanduser()
    
    # Ensure directories exist
    input_path.mkdir(parents=True, exist_ok=True)
    processed_path.mkdir(parents=True, exist_ok=True)
    vault_path.mkdir(parents=True, exist_ok=True)
    
    if args.command == "run":
        run_command(input_path, processed_path, vault_path)
    elif args.command == "watch":
        watch_command(input_path, processed_path, vault_path)
    elif args.command == "status":
        status_command(vault_path)

if __name__ == "__main__":
    main()

