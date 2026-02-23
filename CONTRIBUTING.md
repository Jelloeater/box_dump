# Contributing to package-backup

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Jelloeater/box_dump.git
cd box_dump

# Install dependencies
pip install -e ".[dev,viewer]"

# Or with uv
uv pip install -e ".[dev,viewer]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov --cov-fail-under=50 tests/
```

## Code Style

We use ruff for linting and formatting:

```bash
# Check for issues
ruff check .

# Format code
ruff format .
```

## Adding a New Package Manager

1. Add parser method to `PackageCollector` in `backup.py`
2. Add to `collect_all()` method
3. Add install command in `drift_viewer.py`
4. Add tests

## Commit Messages

Follow conventional commits:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` adding tests
- `chore:` maintenance

## Submitting Changes

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request
