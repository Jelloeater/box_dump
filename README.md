# Package Backup & Drift Viewer

Backup installed packages from multiple package managers to JSON/SQLite, and visualize package drift between machines with a NiceGUI web interface.

## Features

- **Multi-platform package collection**: Works on macOS and Linux
- **Multiple package managers**: brew, apt, snap, flatpak, pip, npm, stew, zb
- **SQLite storage**: Local database for fast queries
- **GitHub sync**: Push backups to a shared repo
- **Drift visualization**: NiceGUI web UI showing package differences
- **Install commands**: Generate commands to sync packages between machines
- **Unified CLI**: Single `box-dump` command with subcommands

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

### Install as CLI tool (recommended)

```bash
# Using uv (recommended)
uv tool install .

# Or using pipx
pipx install .
```

This installs the `box-dump` command globally.

### Development Install

```bash
# Install with all dependencies
uv pip install -e . --system --break-system-packages

# Or with pip
pip install -e ".[dev]"
```

## Usage

### Backup Command

```bash
# Basic backup to default cache (~/.cache/box_dump)
box-dump backup

# Backup to custom directory (useful for git versioning)
box-dump backup --path ~/projects/package-backups

# Backup and push to GitHub
box-dump backup --push --repo "your-username/package-backups"

# Skip SQLite export
box-dump backup --no-sqlite
```

### Viewer Command

```bash
# Run the web UI (default port 8080)
box-dump viewer

# Custom port
box-dump viewer --port 3000
```

Then open http://localhost:8080 in your browser.

### Run Without Installation

```bash
# Using uv
uv run -m box_dump.cli backup
uv run -m box_dump.cli viewer

# Or with specific subcommand
uv run -m box_dump.cli backup --path ~/my-packages
```

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
2. Run backup with `--push --repo "your-username/repo-name"`
3. Each machine backs up to its own JSON files in the repo

## Configuration

### Default Paths

- **JSON cache**: `~/.cache/box_dump/`
- **SQLite database**: `~/.local/share/package-backup/packages.db`
- **Git repo clone**: `~/.cache/package-backup/`

### Override Output Directory

Use `--path` to specify a custom output directory (e.g., a git-initialized folder):

```bash
box-dump backup --path ~/projects/package-backups --push
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]" --system --break-system-packages

# Run tests
pytest

# Lint
ruff check .
```

## License

MIT
