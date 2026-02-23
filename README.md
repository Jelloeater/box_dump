# Package Backup & Drift Viewer

Backup installed packages from multiple package managers to JSON/SQLite, and visualize package drift between machines with a NiceGUI web interface.

## Features

- **Multi-platform package collection**: Works on macOS and Linux
- **Multiple package managers**: brew, apt, snap, flatpak, pip, npm, stew, zb
- **SQLite storage**: Local database for fast queries
- **GitHub sync**: Push backups to a shared repo
- **Drift visualization**: NiceGUI web UI showing package differences
- **Install commands**: Generate commands to sync packages between machines

## Supported Package Managers

| Manager | macOS | Linux | Notes |
|---------|-------|-------|-------|
| brew    | ✅    | ✅    | Linuxbrew supported |
| apt     | ❌    | ✅    | Debian/Ubuntu |
| snap    | ❌    | ✅    | |
| flatpak | ❌    | ✅    | |
| pip     | ✅    | ✅    | |
| npm     | ✅    | ✅    | Global packages |
| stew    | ✅    | ✅    | zauberzeug/stew |
| zb      | ✅    | ✅    | zauberzeug/zb |

## Installation

### Quick Start (uv)

```bash
# Run backup
uv run --script backup.py

# Push to GitHub
uv run --script backup.py --push --repo "your-username/package-backups"

# Run drift viewer
uv run --script drift_viewer.py
```

### With pyproject.toml

```bash
# Install dependencies
pip install -e ".[viewer]"

# Or with uv
uv pip install -e ".[viewer]"

# Run
python backup.py
python drift_viewer.py
```

## Usage

### Backup Script

```bash
# Basic backup (creates JSON files locally)
python backup.py

# Backup and push to GitHub
python backup.py --push --repo "username/repo"

# Skip SQLite export
python backup.py --no-sqlite
```

### Drift Viewer

```bash
# Run the web UI
python drift_viewer.py
```

Then open http://localhost:8080 in your browser.

## JSON Output Format

Files are named `{hostname}_{package_manager}.json`:

```json
[
  {"name": "neovim", "version": "0.9.5"},
  {"name": "fish", "version": "3.6.0"},
  {"name": "git", "version": "2.43.0"}
]
```

## GitHub Setup

1. Create a new GitHub repository
2. Update `REPO_URL` in both scripts, or use `--repo` flag
3. Run `backup.py --push` on each machine

## Configuration

Edit these variables in the scripts:

```python
# backup.py
REPO_URL = "https://github.com/{owner}/{repo}.git"
LOCAL_REPO_PATH = Path.home() / ".cache" / "package-backup"

# drift_viewer.py  
REPO_URL = "https://github.com/{owner}/{repo}.git"
LOCAL_REPO_PATH = Path.home() / ".cache" / "package-backup"
DB_PATH = Path.home() / ".local" / "share" / "package-backup" / "packages.db"
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
```

## License

MIT
