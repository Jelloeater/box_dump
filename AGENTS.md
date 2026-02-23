# AGENTS.md - Development Guidelines

## Project Overview

Package-backup is a tool to back up installed packages from multiple package managers to JSON/SQLite, with a NiceGUI web interface to visualize package drift between machines.

## Architecture

```
box_dump/
├── backup.py         # Package collection + GitHub sync
├── drift_viewer.py   # NiceGUI web UI
├── pyproject.toml    # Project config
├── README.md         # Documentation
├── AGENTS.md         # This file
├── .editorconfig     # Editor config
└── tests/
    └── test_backup.py
```

## Key Design Decisions

1. **Single-file scripts**: Both `backup.py` and `drift_viewer.py` are standalone scripts with uv shebangs for easy execution
2. **JSON output**: Simple format `{name, version}` arrays, filenames encode hostname and package manager
3. **SQLite via peewee**: Local database for fast queries and drift analysis
4. **Main branch workflow**: All machines push to main branch with unique filenames

## Package Manager Support

- **macOS**: brew, pip, npm, stew, zb
- **Linux**: brew, apt, snap, flatpak, pip, npm, stew, zb

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

1. Add parser method to `PackageCollector` class in `backup.py`:
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

3. Add install command in `drift_viewer.py` `get_install_command()` function

### Updating dependencies

Update `pyproject.toml` and the shebang dependencies in both scripts.

## Scripts Usage

```bash
# Backup (local only)
uv run --script backup.py

# Backup + push to GitHub
uv run --script backup.py --push --repo "owner/repo"

# Run drift viewer
uv run --script drift_viewer.py
```
