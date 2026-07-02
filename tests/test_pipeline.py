import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from watchdog.events import FileCreatedEvent
from src.watcher import fileSystemChangeHandler, watch_input_directory
from src.enrichment import enrich_note, NoteEnrichment
from src.vault_manager import VaultManager

def test_file_system_change_handler() -> None:
    """Test that the change handler filters files and runs the callback."""
    called_path = None
    
    def callback(path: str) -> None:
        nonlocal called_path
        called_path = path

    handler = fileSystemChangeHandler(callback)
    
    # 1. Test standard txt file event
    txt_event = FileCreatedEvent("input/my_idea.txt")
    handler.on_created(txt_event)
    assert called_path == "input/my_idea.txt"
    
    # Reset
    called_path = None
    
    # 2. Test directory creation event (should be ignored)
    dir_event = FileCreatedEvent("input/my_folder")
    dir_event._is_directory = True # Mark as directory
    handler.on_created(dir_event)
    assert called_path is None

def test_watch_input_directory(tmp_path: Path) -> None:
    """Test watch_input_directory using a background thread and mocked sleep."""
    detected_files = []
    
    def callback(path: str) -> None:
        detected_files.append(Path(path))

    # Control flag to exit the infinite loop inside watch_input_directory
    stop_loop = False
    
    original_sleep = time.sleep
    
    def mock_sleep(seconds: float) -> None:
        if stop_loop:
            raise KeyboardInterrupt
        original_sleep(seconds)

    # Start watcher in a background thread
    watcher_thread = threading.Thread(
        target=watch_input_directory,
        args=(callback, tmp_path)
    )
    
    # Patch time.sleep in src.watcher module
    with patch("src.watcher.time.sleep", side_effect=mock_sleep):
        watcher_thread.start()
        
        # Give the thread a moment to initialize and start the observer
        time.sleep(0.1)
        
        # Write a dummy txt file to the watched directory
        test_file = tmp_path / "new_idea.txt"
        test_file.write_text("my raw dictation content", encoding="utf-8")
        
        # Wait for the watcher to detect and trigger the callback
        time.sleep(0.2)
        
        # Stop the loop and join the thread
        stop_loop = True
        watcher_thread.join(timeout=2.0)
        
    assert len(detected_files) == 1
    assert detected_files[0].name == "new_idea.txt"

@patch("src.enrichment.genai.Client")
def test_enrich_note_success(mock_client_class) -> None:
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    fake_json_response = """{
        "title": "Unique CLI Project",
        "summary": "A command line tool to capture voice notes.",
        "category": "Web Development",
        "status": "Captured",
        "effort": "Low",
        "value": "High",
        "tags": ["python", "cli"],
        "technologies": ["pytest"],
        "next_actions": ["Write a prototype."]
    }"""
    mock_response = MagicMock()
    mock_response.text = fake_json_response

    mock_client.models.generate_content.return_value = mock_response

    result = enrich_note("some raw voice note content", ["Existing Note Title"])
    
    assert isinstance(result, NoteEnrichment)
    assert result.title == "Unique CLI Project"
    assert result.status == "Captured"
    assert "python" in result.tags
    
    mock_client.models.generate_content.assert_called_once()

def test_vault_manager_get_existing_note_titles(tmp_path: Path) -> None:
    (tmp_path / "Note A.md").write_text("content A", encoding="utf-8")
    (tmp_path / "Note B.md").write_text("content B", encoding="utf-8")
    (tmp_path / "Other.txt").write_text("other", encoding="utf-8")
    
    vm = VaultManager(tmp_path)
    titles = vm.get_existing_note_titles()
    
    assert len(titles) == 2
    assert "Note A" in titles
    assert "Note B" in titles
    assert "Other" not in titles

def test_vault_manager_sanitize_title(tmp_path: Path) -> None:
    vm = VaultManager(tmp_path)
    assert vm.sanitize_title("My: Unsanitized/Idea?") == "My Unsanitized Idea"
    assert vm.sanitize_title("   Spaces   ") == "Spaces"
    assert vm.sanitize_title("??//::") == "Untitled Idea"

def test_vault_manager_save_note_to_vault_no_collision(tmp_path: Path) -> None:
    vm = VaultManager(tmp_path)
    note = NoteEnrichment(
        title="My Cool Idea",
        summary="A simple app",
        category="Tech",
        status="Captured",
        effort="Low",
        value="High",
        tags=["Tag 1 with Space"],
        technologies=["tech1"],
        next_actions=["action1"]
    )
    
    saved_path_str = vm.save_note_to_vault(note, "My raw voice input dictation.")
    saved_path = Path(saved_path_str)
    
    assert saved_path.exists()
    assert saved_path.name == "My Cool Idea.md"
    
    content = saved_path.read_text(encoding="utf-8")
    assert "title: \"My Cool Idea\"" in content
    assert "tag1withspace" in content
    assert "## 🎤 Original Dictation" in content
    assert "My raw voice input dictation." in content

def test_vault_manager_save_note_to_vault_with_collision(tmp_path: Path) -> None:
    vm = VaultManager(tmp_path)
    note = NoteEnrichment(
        title="Collision",
        summary="A simple app",
        category="Tech",
        status="Captured",
        effort="Low",
        value="High",
        tags=["tag1"],
        technologies=["tech1"],
        next_actions=["action1"]
    )
    
    path1 = vm.save_note_to_vault(note, "First file content")
    path2 = vm.save_note_to_vault(note, "Second file content")
    
    assert Path(path1).name == "Collision.md"
    assert Path(path2).name == "Collision-1.md"

@patch("src.main.run_command")
def test_cli_argparse_overrides(mock_run) -> None:
    from src.main import main
    import sys
    
    # Simulate: idea-capture --input-dir /tmp/in --processed-dir /tmp/proc --vault-path /tmp/vault run
    test_args = [
        "idea-capture",
        "--input-dir", "/tmp/in",
        "--processed-dir", "/tmp/proc",
        "--vault-path", "/tmp/vault",
        "run"
    ]
    with patch.object(sys, "argv", test_args):
        # Mock Path.mkdir to prevent actual filesystem changes
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            main()
            mock_run.assert_called_once_with(
                Path("/tmp/in"),
                Path("/tmp/proc"),
                Path("/tmp/vault")
            )

@patch("src.main.subprocess.run")
def test_cli_run_sync_integration(mock_run) -> None:
    from src.main import main
    import sys
    
    mock_response = MagicMock()
    mock_response.stdout = "0"
    mock_run.return_value = mock_response
    
    test_args = ["idea-capture", "run"]
    with patch.object(sys, "argv", test_args):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            main()
            mock_run.assert_called_once()
            args_called = mock_run.call_args[0][0]
            assert "osascript" in args_called
            assert "export_ideas.applescript" in args_called[1]