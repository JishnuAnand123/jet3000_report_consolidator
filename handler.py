import os
import shutil
import time
import msvcrt
from datetime import datetime, timedelta
from watchdog.events import FileSystemEventHandler
import config


class FileActionHandler(FileSystemEventHandler):
    def __init__(self, destination_dir, mode_getter, log_callback=None):
        super().__init__()
        self.destination_dir = os.path.abspath(destination_dir)
        self.mode_getter = mode_getter
        self.log_callback = log_callback or print
        self.log_file_path = os.path.abspath(config.LOG_FILE_NAME)
        self._clean_old_logs()

    @property
    def current_mode(self):
        if callable(self.mode_getter):
            return self.mode_getter()
        return self.mode_getter

    def _log(self, status, filename, source_path="", detail=""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{status}] {filename}"
        if source_path:
            log_entry += f" | Source: {source_path}"
        log_entry += f" | Destination: {self.destination_dir}"
        if detail:
            log_entry += f" | {detail}"

        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Failed writing to log file: {e}")

        if self.log_callback:
            self.log_callback(log_entry)

    def _clean_old_logs(self):
        if not os.path.exists(self.log_file_path):
            return

        period = config.LOG_RETENTION_PERIOD.lower()
        days_map = {"daily": 1, "weekly": 7, "monthly": 30}
        max_days = days_map.get(period, 30)
        cutoff_date = datetime.now() - timedelta(days=max_days)

        valid_lines = []
        try:
            with open(self.log_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                if line.startswith("[") and "]" in line:
                    date_str = line[1:20]
                    try:
                        entry_date = datetime.strptime(
                            date_str, "%Y-%m-%d %H:%M:%S")
                        if entry_date >= cutoff_date:
                            valid_lines.append(line)
                    except ValueError:
                        valid_lines.append(line)
                else:
                    valid_lines.append(line)

            with open(self.log_file_path, "w", encoding="utf-8") as f:
                f.writelines(valid_lines)
        except Exception as e:
            print(f"Log maintenance error: {e}")

    def is_file_ready(self, file_path):
        """
        Windows lock check. Verifies external process has released file handles/locks.
        """
        start_time = time.time()
        while time.time() - start_time < config.FILE_LOCK_TIMEOUT:
            try:
                fd = os.open(file_path, os.O_RDWR | os.O_BINARY)
                try:
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                    os.close(fd)
                    return True
                except (IOError, OSError):
                    os.close(fd)
            except (IOError, OSError):
                pass

            time.sleep(config.FILE_CHECK_INTERVAL)
        return False

    def should_process(self, file_path):
        if os.path.isdir(file_path):
            return False
        if config.ALLOWED_EXTENSIONS:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in [e.lower() for e in config.ALLOWED_EXTENSIONS]:
                return False
        return True

    def process_file(self, src_path):
        if not self.should_process(src_path):
            return

        filename = os.path.basename(src_path)
        dest_path = os.path.join(self.destination_dir, filename)

        if os.path.abspath(src_path) == dest_path:
            return

        self._log("DETECTED", filename, source_path=src_path,
                  detail="Waiting for file release")

        if not self.is_file_ready(src_path):
            self._log("SKIPPED", filename, source_path=src_path,
                      detail="File locked by process")
            return

        active_mode = self.current_mode
        try:
            if active_mode == "move":
                shutil.move(src_path, dest_path)
                self._log("SUCCESS_MOVED", filename, source_path=src_path)
            else:
                shutil.copy2(src_path, dest_path)
                self._log("SUCCESS_COPIED", filename, source_path=src_path)
        except Exception as e:
            self._log("FAILURE", filename, source_path=src_path,
                      detail=f"Error: {str(e)}")

    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.process_file(event.dest_path)
