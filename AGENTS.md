# AGENTS.md - Development Guidelines

## Project Overview

Package-backup is a tool to back up installed packages from multiple package managers to JSON/SQLite, with a NiceGUI web interface to visualize package drift between machines.

## Architecture

```
box_dump/
├── box_dump/
│   ├── __init__.py      # Package init, exports CLI
│   ├── cli.py           # Main CLI entry with subcommands
│   └── commands/
│       ├── __init__.py
│       ├── backup.py    # backup subcommand
│       └── viewer.py    # viewer subcommand (NiceGUI)
├── pyproject.toml       # Project config
├── README.md            # Documentation
├── AGENTS.md           # This file
└── tests/
    └── test_backup.py
```

## Key Design Decisions

1. **Unified CLI**: Single `box-dump` command with `backup` and `viewer` subcommands
2. **Installable package**: Can be installed via `uv tool install .` or `pipx install .`
3. **JSON output**: Simple format `{name, version}` arrays, filenames encode hostname and package manager
4. **SQLite via peewee**: Local database for fast queries and drift analysis
5. **Custom output path**: Use `--path` to specify output directory for version-controlled backups
6. **Main branch workflow**: All machines push to main branch with unique filenames

## Package Manager Support

- **macOS**: brew, pip, npm, stew, zb
- **Linux**: brew, apt, snap, flatpak, pip, npm, stew, zb

## Installation

```bash
# Install as CLI tool (recommended)
uv tool install .

# Or using pipx
pipx install .
```

## CLI Usage

```bash
# Backup commands
box-dump backup                    # Default: ~/.cache/box_dump
box-dump backup --path /path       # Custom output directory
box-dump backup --push --repo "owner/repo"
box-dump backup --no-sqlite

# Viewer command
box-dump viewer --port 8080
```

## Testing

Run tests with:

```bash
pytest
```

## Code Style

- Follow PEP 8
- Line length: 100 characters
- Use ruff for linting: `ruff check .`
- Type hints where helpful

## Common Tasks

### Adding a new package manager

1. Add parser method to `PackageCollector` class in `box_dump/commands/backup.py`:
   ```python
   def _parse_newpm(self) -> list[dict]:
       """Parse newpm list."""
       packages = []
       for line in self._run_command("newpm list"):
           # parse output
           packages.append({"name": name, "version": version})
       return packages
   ```

2. Add to `collect_all()` method in appropriate OS block

3. Add install command in `box_dump/commands/viewer.py` `get_install_command()` function

### Updating dependencies

Update `pyproject.toml` dependencies and reinstall:
```bash
uv tool install . --force
```
