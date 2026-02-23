# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-02-22

### Added
- `backup.py`: Package collection from multiple package managers
  - macOS: brew, pip, npm, stew, zb
  - Linux: brew, apt, snap, flatpak, pip, npm, stew, zb
- JSON output with `{name, version}` format
- SQLite export via peewee
- GitHub sync to main branch
- `drift_viewer.py`: NiceGUI web interface
  - Package drift visualization
  - Install command generation
  - Copy to clipboard
- Unit tests with pytest
- GitHub Actions CI/CD workflows
- Pre-commit hooks with ruff

### Dependencies
- peewee >= 3.17.0
- GitPython >= 3.1.40
- nicegui >= 2.0.0 (optional)
- pytest >= 7.0.0 (dev)
- ruff >= 0.1.0 (dev)
