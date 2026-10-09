# ICT File Router & Folder Monitor

A lightweight, multi-instance desktop application for Windows that monitors folders for new or moved files and routes them to a designated target folder in real time.

---

## Technical Specifications & Features
- **Low Overhead:** Native Windows filesystem events (`ReadDirectoryChangesW`) ensure ~0% idle CPU usage.
- **Dynamic Action Switching:** Switch between `Copy` and `Move` modes live without restarting active monitoring.
- **File Lock Safety:** Automatic retry check to prevent reading incomplete or partially written files.
- **Structured Logging:** Tracks `Source`, `Destination`, timestamp, filename, and status tags (`SUCCESS_COPIED`, `SUCCESS_MOVED`, `FAILURE`, `SKIPPED`).
- **Retention Rules:** Automated log file cleanup based on `config.py` settings (`daily`, `weekly`, `monthly`).

---

## Setup & Deployment Guide

### Setup 1: Running as a Python Application (Development / Script Mode)

1. **Open Command Prompt or PowerShell in the root directory:**
   ```cmd
   cd path\to\file_consolidator

2. Create and activate a Python virtual environment:
    python -m venv venv venv\Scripts\activate

3. Install required dependencies:
    pip install -r requirements.txt

4. Run the interface:
    python main_gui.py

