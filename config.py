import os

# Default File Operation Mode: 'copy' or 'move'
DEFAULT_ACTION = "copy"

# UI Toggle Control
ALLOW_ACTION_TOGGLE = True

# Filter by extension (e.g., [".csv", ".log", ".txt"]). Empty list = process ALL files.
ALLOWED_EXTENSIONS = []

# File Lock & Completion Thresholds
FILE_LOCK_TIMEOUT = 10     # Maximum seconds to wait for file write lock
FILE_CHECK_INTERVAL = 0.5   # Seconds between file lock checks

# --- LOGGING CONFIGURATION ---
LOG_FILE_NAME = "monitor.log"

# Log Retention Cleanup Interval: "daily", "weekly", or "monthly"
LOG_RETENTION_PERIOD = "monthly"
