"""CLI entry point for box-dump."""

import argparse
import sys
from pathlib import Path

from box_dump.commands import backup, viewer


def main():
    parser = argparse.ArgumentParser(
        prog="box-dump",
        description="Backup installed packages and visualize drift between machines.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    backup_parser = subparsers.add_parser(
        "backup",
        help="Backup installed packages to JSON and SQLite",
    )
    backup_parser.add_argument(
        "--push",
        action="store_true",
        help="Push to GitHub",
    )
    backup_parser.add_argument(
        "--repo",
        type=str,
        default="https://github.com/{owner}/{repo}.git",
        help="GitHub repository (owner/repo)",
    )
    backup_parser.add_argument(
        "--no-sqlite",
        action="store_true",
        help="Skip SQLite export",
    )
    backup_parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Output directory for JSON files (default: ~/.cache/box_dump)",
    )
    backup_parser.set_defaults(func=backup.main)

    viewer_parser = subparsers.add_parser(
        "viewer",
        help="Launch the NiceGUI drift viewer",
    )
    viewer_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run the viewer on",
    )
    viewer_parser.set_defaults(func=viewer.main)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)
