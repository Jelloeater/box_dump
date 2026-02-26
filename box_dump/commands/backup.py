"""Backup subcommand for box-dump."""

import argparse
import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path

from git import Repo
from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    SqliteDatabase,
)

HOSTNAME = platform.node()
REPO_URL = "https://github.com/{owner}/{repo}.git"
LOCAL_REPO_PATH = Path.home() / ".cache" / "package-backup"
CACHE_PATH = Path.home() / ".cache" / "box_dump"
DB_PATH = Path.home() / ".local" / "share" / "package-backup" / "packages.db"


class PackageCollector:
    """Collects installed packages from various package managers."""

    def __init__(self):
        self.hostname = platform.node()
        self.os_type = "darwin" if platform.system() == "Darwin" else "linux"

    def _run_command(self, cmd: str) -> list[str]:
        """Run a command and return output as list of lines."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip().split("\n")
            return []
        except Exception:
            return []

    def _parse_brew(self) -> list[dict]:
        """Parse brew list --versions output."""
        packages = []
        for line in self._run_command("brew list --versions"):
            if line.strip():
                parts = line.strip().split()
                name = parts[0]
                version = parts[1] if len(parts) > 1 else None
                packages.append({"name": name, "version": version})
        return packages

    def _parse_pip(self) -> list[dict]:
        """Parse pip list JSON output."""
        packages = []
        try:
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for pkg in data:
                    packages.append({"name": pkg["name"], "version": pkg["version"]})
        except Exception:
            pass
        return packages

    def _parse_npm(self) -> list[dict]:
        """Parse npm list -g --depth=0 output."""
        packages = []
        for line in self._run_command("npm list -g --depth=0"):
            if line.strip() and not line.startswith("npm"):
                parts = line.strip().split("@")
                if parts:
                    name = parts[0].strip()
                    version = parts[1].strip() if len(parts) > 1 else None
                    if name:
                        packages.append({"name": name, "version": version})
        return packages

    def _parse_apt(self) -> list[dict]:
        """Parse apt list --manual-installed output."""
        packages = []
        for line in self._run_command("apt list --manual-installed"):
            if line and not line.startswith("Listing") and "/" in line:
                parts = line.split("/")
                name = parts[0]
                version_info = parts[1].split() if len(parts) > 1 else []
                version = version_info[0] if version_info else None
                packages.append({"name": name, "version": version})
        return packages

    def _parse_snap(self) -> list[dict]:
        """Parse snap list output."""
        packages = []
        for line in self._run_command("snap list"):
            if line and not line.startswith("Name") and not line.startswith("snap"):
                parts = line.split()
                if len(parts) >= 2:
                    packages.append({"name": parts[0], "version": parts[1]})
        return packages

    def _parse_flatpak(self) -> list[dict]:
        """Parse flatpak list output."""
        packages = []
        for line in self._run_command("flatpak list"):
            if line and not line.startswith("Name"):
                parts = line.split()
                if len(parts) >= 2:
                    packages.append({"name": parts[0], "version": parts[1]})
        return packages

    def _parse_stew(self) -> list[dict]:
        """Parse stew list --tags output."""
        packages = []
        for line in self._run_command("stew list --tags"):
            if line.strip() and not line.startswith("ID"):
                parts = line.strip().split()
                if parts:
                    name = parts[0]
                    version = parts[1] if len(parts) > 1 else None
                    packages.append({"name": name, "version": version})
        return packages

    def _parse_zb(self) -> list[dict]:
        """Parse zb list output."""
        packages = []
        for line in self._run_command("zb list"):
            if line.strip():
                parts = line.strip().split()
                if parts:
                    name = parts[0]
                    version = parts[1] if len(parts) > 1 else None
                    packages.append({"name": name, "version": version})
        return packages

    def collect_all(self) -> dict[str, list[dict]]:
        """Collect all packages based on OS."""
        packages = {}

        if self.os_type == "darwin":
            packages["brew"] = self._parse_brew()
            packages["pip"] = self._parse_pip()
            packages["npm"] = self._parse_npm()
            packages["stew"] = self._parse_stew()
            packages["zb"] = self._parse_zb()
        elif self.os_type == "linux":
            packages["brew"] = self._parse_brew()
            packages["apt"] = self._parse_apt()
            packages["snap"] = self._parse_snap()
            packages["flatpak"] = self._parse_flatpak()
            packages["pip"] = self._parse_pip()
            packages["npm"] = self._parse_npm()
            packages["stew"] = self._parse_stew()
            packages["zb"] = self._parse_zb()

        return packages


class GitManager:
    """Manages git operations for the backup repository."""

    def __init__(self, repo_url: str, local_path: Path):
        self.repo_url = repo_url
        self.local_path = local_path

    def clone_or_pull(self) -> Repo:
        """Clone repo if not exists, otherwise pull."""
        if self.local_path.exists():
            repo = Repo(self.local_path)
            origin = repo.remotes.origin
            origin.pull()
        else:
            self.local_path.parent.mkdir(parents=True, exist_ok=True)
            repo = Repo.clone_from(self.repo_url, self.local_path)

        try:
            repo.git.checkout("main")
        except Exception:
            pass

        return repo

    def checkout_branch(self, repo: Repo) -> None:
        """Ensure we're on main branch."""
        try:
            repo.git.checkout("main")
        except Exception:
            pass

    def commit_and_push(self, repo: Repo, files: list[Path], message: str) -> None:
        """Add, commit, and push files to main branch."""
        for f in files:
            if f.exists():
                import shutil

                dest = self.local_path / f.name
                shutil.copy2(f, dest)
                repo.index.add([str(dest)])

        if repo.index.diff("HEAD") or repo.untracked_files:
            repo.index.commit(message)
            origin = repo.remotes.origin
            origin.push()


def setup_database(db_path: Path):
    """Setup peewee database and models."""
    db = SqliteDatabase(db_path)

    class Host(Model):
        hostname = CharField(unique=True)
        os = CharField()
        last_updated = DateTimeField()

        class Meta:
            database = db

    class PackageManager(Model):
        name = CharField()

        class Meta:
            database = db

    class Package(Model):
        host = ForeignKeyField(Host)
        package_manager = ForeignKeyField(PackageManager)
        name = CharField()
        version = CharField(null=True)

        class Meta:
            database = db

    db.connect()
    db.create_tables([Host, PackageManager, Package])

    return db, Host, PackageManager, Package


def export_to_sqlite(
    db: SqliteDatabase,
    Host: type[Model],
    PackageManager: type[Model],
    Package: type[Model],
    packages: dict[str, list[dict]],
    os_type: str,
) -> None:
    """Export collected packages to SQLite."""
    host, _ = Host.get_or_create(
        hostname=HOSTNAME,
        defaults={"os": os_type, "last_updated": datetime.now()},
    )
    host.last_updated = datetime.now()
    host.save()

    Package.delete().where(Package.host == host.id).execute()

    for pm_name, pkgs in packages.items():
        pm, _ = PackageManager.get_or_create(name=pm_name)

        for pkg in pkgs:
            Package.get_or_create(
                host=host.id,
                package_manager=pm.id,
                name=pkg["name"],
                defaults={"version": pkg.get("version")},
            )


def main(args: argparse.Namespace):
    """Main entry point for backup subcommand."""
    collector = PackageCollector()
    packages = collector.collect_all()

    output_path = args.path if args.path else CACHE_PATH
    output_path.mkdir(parents=True, exist_ok=True)

    for pm_name, pkgs in packages.items():
        output_file = output_path / f"{collector.hostname}_{pm_name}.json"
        with open(output_file, "w") as f:
            json.dump(pkgs, f, indent=2)
        print(f"Wrote {len(pkgs)} packages to {output_file}")

    if not args.no_sqlite:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        db, Host, PackageManager, Package = setup_database(DB_PATH)
        export_to_sqlite(db, Host, PackageManager, Package, packages, collector.os_type)
        print(f"Exported to SQLite: {DB_PATH}")

    if args.push:
        repo_url = f"https://github.com/{args.repo}.git"
        git_mgr = GitManager(repo_url, LOCAL_REPO_PATH)
        repo = git_mgr.clone_or_pull()

        json_files = list(output_path.glob(f"{collector.hostname}_*.json"))
        git_mgr.commit_and_push(
            repo,
            json_files,
            f"Update packages for {collector.hostname}",
        )
        print(f"Pushed to GitHub: {args.repo}")
