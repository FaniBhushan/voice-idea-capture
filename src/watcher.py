import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import Callable


class fileSystemChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
    def on_created(self, event):
        if not event.is_directory:
            if event.src_path.endswith('.txt') or event.src_path.endswith('.md'):
                try:
                    self.callback(event.src_path)
                except Exception as e:
                    print(f"Error processing file {event.src_path}: {e}")
                

def watch_input_directory(callback_func: Callable[[Path],None], watch_dir: Path) -> None:
    event_handler = fileSystemChangeHandler(callback_func)
    observer = Observer()
    observer.schedule(event_handler, str(watch_dir), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


