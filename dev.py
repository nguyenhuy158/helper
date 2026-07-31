"""Development file watcher for auto-reinstalling the package."""

import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ChangeHandler(FileSystemEventHandler):
    """Handler for file system events to trigger package reinstall."""

    def on_modified(self, event):
        """Handle file modification events."""
        src_path = str(event.src_path)
        if src_path.endswith(".py") and not any(x in src_path for x in ["__pycache__", ".git"]):
            print("\nDetected changes. Reinstalling package...")
            try:
                subprocess.run(["pip", "install", "-e", "."], check=True)
                print("Package reinstalled successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Error reinstalling package: {e}")


def main():
    """Start the file watcher."""
    print("Watching for file changes...")
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
