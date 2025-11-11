import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py") and not any(
            x in event.src_path for x in ["__pycache__", ".git"]
        ):
            print("\nDetected changes. Reinstalling package...")
            try:
                subprocess.run(["pip", "install", "-e", "."], check=True)
                print("Package reinstalled successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Error reinstalling package: {e}")


def main():
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
