# ICT Log Parsing Specifications

This application writes output events to `monitor.log` located in the application runtime directory.

## Log Entry Structure
`[TIMESTAMP] [STATUS_TAG] FILENAME | DETAILS`

### Status Tags
1. `SUCCESS_COPIED` - File copied to destination successfully.
2. `SUCCESS_MOVED` - File moved to destination successfully.
3. `FAILURE` - File operation failed (permissions, missing file, disk space).
4. `SKIPPED` - File lock timeout exceeded or extension not matched.
5. `DETECTED` - New file identified, file lock wait initiated.

## Parsing Instructions for External Scripts/Bots

### Regular Expression Pattern
Use this standard regex pattern to extract log components:
`^\[(?P<timestamp>.*?)\] \[(?P<status>.*?)\] (?P<filename>[^|]+)(?: \| (?P<details>.*))?$`

### Target Statuses
- **Successes:** Filter lines containing `SUCCESS_COPIED` or `SUCCESS_MOVED`.
- **Failures:** Filter lines containing `FAILURE` or `SKIPPED`.