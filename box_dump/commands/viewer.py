"""Viewer subcommand for box-dump - NiceGUI app to visualize package drift."""

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

from nicegui import ui
from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    SqliteDatabase,
)

REPO_URL = "https://github.com/{owner}/{repo}.git"
LOCAL_REPO_PATH = Path.home() / ".cache" / "package-backup"
DB_PATH = Path.home() / ".local" / "share" / "package-backup" / "packages.db"

db = None
Host = None
PackageManager = None
Package = None
table = None
drift_label = None
missing_table = None
selected_host = {"name": None}


def setup_db():
    """Setup peewee database and models."""
    global db, Host, PackageManager, Package

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    database = SqliteDatabase(DB_PATH)

    class HostModel(Model):
        hostname = CharField(unique=True)
        os = CharField()
        last_updated = DateTimeField()

        class Meta:
            database = database

    class PackageManagerModel(Model):
        name = CharField()

        class Meta:
            database = database

    class PackageModel(Model):
        host = ForeignKeyField(HostModel)
        package_manager = ForeignKeyField(PackageManagerModel)
        name = CharField()
        version = CharField(null=True)

        class Meta:
            database = database

    database.connect()
    database.create_tables([HostModel, PackageManagerModel, PackageModel])

    db = database
    Host = HostModel
    PackageManager = PackageManagerModel
    Package = PackageModel

    return database


def clone_or_pull():
    """Clone or pull from repo."""
    if not LOCAL_REPO_PATH.exists():
        LOCAL_REPO_PATH.parent.mkdir(parents=True, exist_ok=True)
        Repo = __import__("git").Repo
        Repo.clone_from(REPO_URL, LOCAL_REPO_PATH)
    else:
        subprocess.run(["git", "pull"], cwd=LOCAL_REPO_PATH, capture_output=True)


def load_packages_from_repo() -> dict[str, dict[str, list[dict]]]:
    """Load package JSON files from the repo.

    Files are named: {hostname}_{package_manager}.json
    e.g., JesseDev_brew.json, JesseDev_apt.json
    """
    packages_by_host = {}

    if not LOCAL_REPO_PATH.exists():
        return packages_by_host

    for json_file in LOCAL_REPO_PATH.glob("*.json"):
        stem = json_file.stem
        if "_" not in stem:
            continue

        parts = stem.rsplit("_", 1)
        if len(parts) != 2:
            continue

        hostname, pm_name = parts

        try:
            with open(json_file) as f:
                pkgs = json.load(f)
        except Exception:
            continue

        if hostname not in packages_by_host:
            packages_by_host[hostname] = {}
        packages_by_host[hostname][pm_name] = pkgs

    return packages_by_host


def get_install_command(pkg_name: str, target_os: str, package_manager: str | None = None) -> str:
    """Generate install command for a package."""
    if package_manager:
        if package_manager == "brew":
            return f"brew install {pkg_name}"
        elif package_manager == "apt":
            return f"sudo apt install {pkg_name}"
        elif package_manager == "pip":
            return f"pip install {pkg_name}"
        elif package_manager == "npm":
            return f"npm install -g {pkg_name}"
        elif package_manager == "snap":
            return f"sudo snap install {pkg_name}"
        elif package_manager == "flatpak":
            return f"flatpak install {pkg_name}"
        elif package_manager == "stew":
            return f"stew install {pkg_name}"
        elif package_manager == "zb":
            return f"zb install {pkg_name}"

    if target_os == "darwin":
        return f"brew install {pkg_name}"
    else:
        return f"sudo apt install {pkg_name}"


def refresh_data():
    """Refresh data from repo and rebuild DB."""
    global table, drift_label
    try:
        clone_or_pull()
        all_packages = load_packages_from_repo()

        database = setup_db()

        Host.delete().execute()

        for hostname, packages in all_packages.items():
            host, _ = Host.get_or_create(
                hostname=hostname,
                defaults={"os": "linux", "last_updated": datetime.now()},
            )

            for pm_name, pkgs in packages.items():
                pm, _ = PackageManager.get_or_create(name=pm_name)

                for pkg in pkgs:
                    Package.create(
                        host=host,
                        package_manager=pm,
                        name=pkg["name"],
                        version=pkg.get("version"),
                    )

        ui.notify("Data refreshed!", type="positive")
        load_table_data()

    except Exception as e:
        ui.notify(f"Error: {e}", type="negative")


def load_table_data():
    """Load and display hosts in table."""
    global table, drift_label
    try:
        database = setup_db()
        hosts = Host.select()

        rows = []
        for host in hosts:
            count = Package.select().where(Package.host == host).count()
            rows.append(
                {
                    "hostname": host.hostname,
                    "os": host.os,
                    "packages": count,
                    "last_updated": host.last_updated.strftime("%Y-%m-%d %H:%M")
                    if host.last_updated
                    else "Never",
                }
            )

        table.rows = rows

        all_packages = load_packages_from_repo()
        drift_label.set_text(f"Total hosts: {len(all_packages)}")

    except Exception as e:
        ui.notify(f"Error loading data: {e}", type="negative")


def on_row_click(e):
    """Handle row click to show drift details."""
    global selected_host, missing_table, drift_label
    selected_host["name"] = e.value["hostname"]

    all_packages = load_packages_from_repo()
    hosts = list(all_packages.keys())

    host_data = all_packages.get(selected_host["name"], {})
    other_hosts = [h for h in hosts if h != selected_host["name"]]

    host_pkgs = set()
    for pm_pkgs in host_data.values():
        host_pkgs.update(pkg["name"] for pkg in pm_pkgs)

    missing = []
    for other_host in other_hosts:
        other_data = all_packages.get(other_host, {})
        other_pkgs = set()
        for pm_pkgs in other_data.values():
            other_pkgs.update(pkg["name"] for pkg in pm_pkgs)

        unique_to_other = other_pkgs - host_pkgs
        for pkg_name in sorted(unique_to_other):
            for pm_name, pkgs in other_data.items():
                if any(p["name"] == pkg_name for p in pkgs):
                    missing.append(
                        {
                            "name": pkg_name,
                            "pm": pm_name,
                            "command": get_install_command(pkg_name, "linux", pm_name),
                        }
                    )
                    break

    missing.sort(key=lambda x: x["name"])

    drift_label.set_text(f"Selected: {selected_host['name']} | Unique packages: {len(missing)}")

    missing_table.rows = missing


async def copy_commands():
    """Copy selected install commands to clipboard."""
    global selected_host, missing_table
    if not selected_host["name"]:
        ui.notify("No host selected", type="warning")
        return

    all_packages = load_packages_from_repo()
    hosts = list(all_packages.keys())

    host_data = all_packages.get(selected_host["name"], {})
    other_hosts = [h for h in hosts if h != selected_host["name"]]

    host_pkgs = set()
    for pm_pkgs in host_data.values():
        host_pkgs.update(pkg["name"] for pkg in pm_pkgs)

    commands = []
    for other_host in other_hosts:
        other_data = all_packages.get(other_host, {})
        other_pkgs = set()
        for pm_pkgs in other_data.values():
            other_pkgs.update(pkg["name"] for pkg in pm_pkgs)

        unique_to_other = other_pkgs - host_pkgs
        for pkg_name in sorted(unique_to_other):
            for pm_name, pkgs in other_data.items():
                if any(p["name"] == pkg_name for p in pkgs):
                    commands.append(get_install_command(pkg_name, "linux", pm_name))
                    break

    commands_text = "\n".join(commands)
    await ui.run_javascript(f"navigator.clipboard.writeText({json.dumps(commands_text)})")
    ui.notify(f"Copied {len(commands)} commands!", type="positive")


def create_ui():
    """Create the NiceGUI UI."""
    global table, drift_label, missing_table

    ui.page_title("Package Drift Viewer")

    with ui.header():
        ui.label("Package Drift Viewer").style("font-size: 1.5em; font-weight: bold")
        with ui.row():
            ui.button("Refresh", on_click=refresh_data).props("flat")

    with ui.row().style("width: 100%; padding: 10px"):
        drift_label = ui.label("Loading...").style("font-weight: bold")

    table = ui.table(
        columns=[
            {"name": "hostname", "label": "Host", "field": "hostname", "align": "left"},
            {"name": "os", "label": "OS", "field": "os", "align": "left"},
            {"name": "packages", "label": "Packages", "field": "packages", "align": "right"},
            {
                "name": "last_updated",
                "label": "Last Updated",
                "field": "last_updated",
                "align": "left",
            },
        ],
        rows=[],
        row_key="hostname",
    ).style("width: 100%")
    table.on("rowClick", on_row_click)

    missing_table = ui.table(
        columns=[
            {"name": "name", "label": "Package", "field": "name", "align": "left"},
            {"name": "pm", "label": "Manager", "field": "pm", "align": "left"},
            {"name": "command", "label": "Install Command", "field": "command", "align": "left"},
        ],
        rows=[],
    ).style("width: 100%")

    with ui.row():
        ui.button("Copy All Commands", on_click=copy_commands).props("color=primary")

    load_table_data()


def main(args: argparse.Namespace):
    """Main entry point for viewer subcommand."""
    create_ui()
    ui.run(port=args.port)
