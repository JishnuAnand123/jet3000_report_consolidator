import os
import time
import shutil
import unittest
import msvcrt
from monitor import FolderMonitorEngine


def print_header(title):
    print("\n" + "=" * 80)
    print(f" RUNNING TEST: {title}")
    print("=" * 80)


class TestFileMonitorSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.abspath("test_environment")
        cls.source1 = os.path.join(cls.test_dir, "source1")
        cls.source2 = os.path.join(cls.test_dir, "source2")
        cls.destination = os.path.join(cls.test_dir, "destination")

        os.makedirs(cls.source1, exist_ok=True)
        os.makedirs(cls.source2, exist_ok=True)
        os.makedirs(cls.destination, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        time.sleep(0.5)
        if os.path.exists(cls.test_dir):
            try:
                shutil.rmtree(cls.test_dir)
            except Exception as e:
                print(f"Teardown cleanup warning: {e}")

    def setUp(self):
        self.active_mode = "copy"
        self.engine = FolderMonitorEngine(
            source_folders=[self.source1, self.source2],
            destination_folder=self.destination,
            mode_getter=lambda: self.active_mode,
            log_callback=lambda msg: print(f"  --> {msg}")
        )
        self.engine.start()
        time.sleep(0.5)

    def tearDown(self):
        self.engine.stop()
        print("-" * 80 + "\n")
        for folder in [self.source1, self.source2, self.destination]:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    path = os.path.join(folder, f)
                    try:
                        if os.path.isfile(path):
                            os.remove(path)
                        elif os.path.isdir(path):
                            shutil.rmtree(path)
                    except Exception as e:
                        print(f"File remove warning in tearDown: {e}")

    def test_01_copy_mode_file_creation(self):
        """Verify that creating a file in Source copies it to Destination."""
        print_header("TEST 01: COPY MODE FILE CREATION")
        self.active_mode = "copy"
        file_name = "test_copy.txt"
        src_file = os.path.join(self.source1, file_name)
        dest_file = os.path.join(self.destination, file_name)

        with open(src_file, "w") as f:
            f.write("ICT Test Payload Copy")

        time.sleep(1.5)

        self.assertTrue(os.path.exists(dest_file),
                        "File was not copied to destination.")
        self.assertTrue(os.path.exists(src_file),
                        "Source file should remain in Copy mode.")

    def test_02_move_mode_file_creation(self):
        """Verify that creating a file in Move mode moves it to Destination."""
        print_header("TEST 02: MOVE MODE FILE CREATION")
        self.active_mode = "move"
        file_name = "test_move.txt"
        src_file = os.path.join(self.source2, file_name)
        dest_file = os.path.join(self.destination, file_name)

        with open(src_file, "w") as f:
            f.write("ICT Test Payload Move")

        time.sleep(1.5)

        self.assertTrue(os.path.exists(dest_file),
                        "File was not moved to destination.")
        self.assertFalse(os.path.exists(src_file),
                         "Source file should be removed in Move mode.")

    def test_03_slow_writing_file(self):
        """Simulate an ICT process writing a large file over 2 seconds while holding an OS file lock."""
        print_header("TEST 03: SLOW LOCKED FILE WRITE HANDLING")
        self.active_mode = "copy"
        file_name = "slow_ict_data.bin"
        src_file = os.path.join(self.source1, file_name)
        dest_file = os.path.join(self.destination, file_name)

        fd = os.open(src_file, os.O_RDWR | os.O_CREAT | os.O_BINARY)
        try:
            os.write(fd, b"Header Information\n")
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)

            time.sleep(1.5)

            os.lseek(fd, 0, os.SEEK_END)
            os.write(fd, b"Footer Information\n")

            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        finally:
            os.close(fd)

        time.sleep(2.0)

        self.assertTrue(os.path.exists(dest_file),
                        "Destination file missing after lock release.")
        with open(dest_file, "rb") as f:
            content = f.read()
        self.assertIn(b"Footer Information", content,
                      "Copied file was incomplete/corrupted.")

    def test_04_ignore_subdirectories(self):
        """Verify subfolder contents are ignored (top-level check only)."""
        print_header("TEST 04: IGNORE SUBDIRECTORIES")
        subfolder = os.path.join(self.source1, "nested_folder")
        os.makedirs(subfolder, exist_ok=True)

        nested_file = os.path.join(subfolder, "nested.txt")
        dest_nested_file = os.path.join(self.destination, "nested.txt")

        with open(nested_file, "w") as f:
            f.write("Nested directory data")

        time.sleep(1.5)

        self.assertFalse(os.path.exists(dest_nested_file),
                         "Files inside subfolders should be ignored.")


if __name__ == "__main__":
    unittest.main()
