import re
from pathlib import Path
from src.enrichment import NoteEnrichment

class VaultManager:
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path

    def get_existing_note_titles(self) -> list[str]:
        """Scans the vault directory and returns all note filenames (sans .md)."""
        if not self.vault_path.exists():
            return []
        return [f.stem for f in self.vault_path.glob("*.md") if f.is_file()]

    def sanitize_title(self, title: str) -> str:
        """Sanitizes the note title to be safe for filenames."""
        # Replace illegal filename characters with space
        sanitized = re.sub(r'[\\/:?*"<>|]', ' ', title)
        # Collapse multiple spaces and strip
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        return sanitized if sanitized else "Untitled Idea"

    def format_note(self, note: NoteEnrichment, raw_content: str) -> str:
        """Formats the NoteEnrichment object and raw content into Markdown with frontmatter."""
        # Sanitize tags to be valid Obsidian tags (no spaces, only allowed symbols like /_-)
        cleaned_tags = []
        for tag in note.tags:
            # Remove spaces: "Photo Management" -> "PhotoManagement"
            # Strip out symbols not allowed in tags
            t_clean = re.sub(r'[^a-zA-Z0-9/_-]', '', tag.replace(" ", "")).lower()
            if t_clean:
                cleaned_tags.append(t_clean)

        # Construct YAML frontmatter manually to avoid third-party dependencies (like PyYAML)
        yaml_lines = ["---"]
        yaml_lines.append(f"title: \"{note.title}\"")
        yaml_lines.append(f"summary: \"{note.summary}\"")
        yaml_lines.append(f"category: \"{note.category}\"")
        yaml_lines.append(f"status: \"{note.status}\"")
        yaml_lines.append(f"effort: \"{note.effort}\"")
        yaml_lines.append(f"value: \"{note.value}\"")
        
        yaml_lines.append("tags:")
        for tag in cleaned_tags:
            yaml_lines.append(f"  - {tag}")
            
        yaml_lines.append("technologies:")
        for tech in note.technologies:
            yaml_lines.append(f"  - {tech}")
            
        yaml_lines.append("next_actions:")
        for action in note.next_actions:
            yaml_lines.append(f"  - {action}")
        yaml_lines.append("---")
        frontmatter = "\n".join(yaml_lines)

        # Format body content
        tags_str = ", ".join([f"#{t}" for t in cleaned_tags]) if cleaned_tags else "None"
        tech_list = "\n".join([f"- {t}" for t in note.technologies]) if note.technologies else "- None"
        actions_list = "\n".join([f"- [ ] {a}" for a in note.next_actions]) if note.next_actions else "- [ ] None"

        markdown_content = f"""{frontmatter}

# {note.title}

## 📝 Summary
{note.summary}

## 🏷️ Category & Tags
- **Category:** {note.category}
- **Tags:** {tags_str}

## 📊 Metadata
- **Status:** {note.status}
- **Effort:** {note.effort}
- **Value:** {note.value}

## 🛠️ Technologies
{tech_list}

## 📋 Next Actions
{actions_list}

## 🎤 Original Dictation
```text
{raw_content.strip()}
```
"""
        return markdown_content

    def save_note_to_vault(self, note: NoteEnrichment, raw_content: str) -> str:
        """Saves the note to the vault, resolving collisions and returning the file path as a string."""
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        base_title = self.sanitize_title(note.title)
        file_path = self.vault_path / f"{base_title}.md"
        
        counter = 1
        while file_path.exists():
            file_path = self.vault_path / f"{base_title}-{counter}.md"
            counter += 1
            
        markdown_content = self.format_note(note, raw_content)
        file_path.write_text(markdown_content, encoding="utf-8")
        
        return str(file_path.resolve())