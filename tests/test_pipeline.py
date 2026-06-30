import threading
import time
from pathlib import Path
from unittest.mock import patch
from watchdog.events import FileCreatedEvent
from src.watcher import fileSystemChangeHandler, watch_input_directory

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
