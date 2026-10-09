import os
from watchdog.observers import Observer
from handler import FileActionHandler


class FolderMonitorEngine:
    def __init__(self, source_folders, destination_folder, mode_getter="copy", log_callback=None):
        self.source_folders = [os.path.abspath(f) for f in source_folders]
        self.destination_folder = os.path.abspath(destination_folder)
        self.mode_getter = mode_getter
        self.log_callback = log_callback
        self.observer = Observer()

    def start(self):
        handler = FileActionHandler(
            destination_dir=self.destination_folder,
            mode_getter=self.mode_getter,
            log_callback=self.log_callback
        )
        for folder in self.source_folders:
            if os.path.exists(folder):
                self.observer.schedule(handler, path=folder, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
