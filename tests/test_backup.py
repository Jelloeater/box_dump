"""Tests for backup.py package collection functionality."""

import json
import platform
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestPackageCollector:
    """Tests for PackageCollector class."""

    def test_hostname_detection(self):
        """Test that hostname is correctly detected."""
        from box_dump.commands.backup import PackageCollector

        collector = PackageCollector()
        assert collector.hostname == platform.node()
        assert collector.hostname != ""

    def test_os_detection(self):
        """Test that OS type is correctly detected."""
        from box_dump.commands.backup import PackageCollector

        collector = PackageCollector()
        assert collector.os_type in ["darwin", "linux", "windows"]

    @patch("box_dump.commands.backup.subprocess.run")
    def test_parse_brew(self, mock_run):
        """Test parsing brew list output."""
        from box_dump.commands.backup import PackageCollector

        mock_run.return_value = MagicMock(
            stdout="neovim 0.9.5\nfish 3.6.0\ngit 2.43.0\n",
            returncode=0,
        )

        collector = PackageCollector()
        result = collector._parse_brew()

        assert len(result) == 3
        assert result[0] == {"name": "neovim", "version": "0.9.5"}
        assert result[1] == {"name": "fish", "version": "3.6.0"}
        assert result[2] == {"name": "git", "version": "2.43.0"}

    @patch("box_dump.commands.backup.subprocess.run")
    def test_parse_pip(self, mock_run):
        """Test parsing pip list JSON output."""
        from box_dump.commands.backup import PackageCollector

        mock_output = json.dumps(
            [
                {"name": "requests", "version": "2.31.0"},
                {"name": "flask", "version": "3.0.0"},
            ]
        )
        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)

        collector = PackageCollector()
        result = collector._parse_pip()

        assert len(result) == 2
        assert result[0] == {"name": "requests", "version": "2.31.0"}
        assert result[1] == {"name": "flask", "version": "3.0.0"}

    @patch("box_dump.commands.backup.subprocess.run")
    def test_parse_apt(self, mock_run):
        """Test parsing apt list output."""
        from box_dump.commands.backup import PackageCollector

        mock_run.return_value = MagicMock(
            stdout="git/jammy,now 1:2.43.0-1 amd64 [installed]\n"
            "neovim/jammy,now 0.9.5-1 amd64 [installed]\n",
            returncode=0,
        )

        collector = PackageCollector()
        result = collector._parse_apt()

        assert len(result) == 2
        assert result[0]["name"] == "git"

    @patch("box_dump.commands.backup.subprocess.run")
    def test_run_command_handles_empty(self, mock_run):
        """Test that _run_command handles empty output."""
        from box_dump.commands.backup import PackageCollector

        mock_run.return_value = MagicMock(stdout="", returncode=0)

        collector = PackageCollector()
        result = collector._run_command("some command")

        assert result == [""]

    @patch("box_dump.commands.backup.subprocess.run")
    def test_run_command_handles_error(self, mock_run):
        """Test that _run_command handles command errors gracefully."""
        from box_dump.commands.backup import PackageCollector

        mock_run.side_effect = Exception("Command not found")

        collector = PackageCollector()
        result = collector._run_command("nonexistent")

        assert result == []

    @patch("box_dump.commands.backup.platform.system")
    def test_collect_all_darwin(self, mock_system):
        """Test collecting all packages on macOS."""
        from box_dump.commands.backup import PackageCollector

        mock_system.return_value = "Darwin"

        with patch.object(PackageCollector, "_parse_brew", return_value=[{"name": "git"}]):
            with patch.object(PackageCollector, "_parse_pip", return_value=[]):
                with patch.object(PackageCollector, "_parse_npm", return_value=[]):
                    with patch.object(PackageCollector, "_parse_stew", return_value=[]):
                        with patch.object(PackageCollector, "_parse_zb", return_value=[]):
                            collector = PackageCollector()
                            result = collector.collect_all()

        assert "brew" in result
        assert "pip" in result
        assert "npm" in result
        assert "stew" in result
        assert "zb" in result

    @patch("box_dump.commands.backup.platform.system")
    def test_collect_all_linux(self, mock_system):
        """Test collecting all packages on Linux."""
        from box_dump.commands.backup import PackageCollector

        mock_system.return_value = "Linux"

        with patch.object(PackageCollector, "_parse_brew", return_value=[]):
            with patch.object(PackageCollector, "_parse_apt", return_value=[{"name": "git"}]):
                with patch.object(PackageCollector, "_parse_snap", return_value=[]):
                    with patch.object(PackageCollector, "_parse_flatpak", return_value=[]):
                        with patch.object(PackageCollector, "_parse_pip", return_value=[]):
                            with patch.object(PackageCollector, "_parse_npm", return_value=[]):
                                with patch.object(PackageCollector, "_parse_stew", return_value=[]):
                                    with patch.object(
                                        PackageCollector, "_parse_zb", return_value=[]
                                    ):
                                        collector = PackageCollector()
                                        result = collector.collect_all()

        assert "brew" in result
        assert "apt" in result
        assert "snap" in result
        assert "flatpak" in result
        assert "pip" in result
        assert "npm" in result
        assert "stew" in result
        assert "zb" in result


class TestGitManager:
    """Tests for GitManager class."""

    def test_init(self):
        """Test GitManager initialization."""
        from box_dump.commands.backup import GitManager

        gm = GitManager("https://github.com/user/repo.git", Path("/tmp/test"))

        assert gm.repo_url == "https://github.com/user/repo.git"
        assert gm.local_path == Path("/tmp/test")


class TestInstallCommands:
    """Tests for install command generation in drift_viewer."""

    def test_brew_install_command(self):
        """Test brew install command generation."""
        from box_dump.commands.viewer import get_install_command

        result = get_install_command("neovim", "darwin", "brew")
        assert result == "brew install neovim"

    def test_apt_install_command(self):
        """Test apt install command generation."""
        from box_dump.commands.viewer import get_install_command

        result = get_install_command("git", "linux", "apt")
        assert result == "sudo apt install git"

    def test_pip_install_command(self):
        """Test pip install command generation."""
        from box_dump.commands.viewer import get_install_command

        result = get_install_command("requests", "linux", "pip")
        assert result == "pip install requests"

    def test_npm_install_command(self):
        """Test npm install command generation."""
        from box_dump.commands.viewer import get_install_command

        result = get_install_command("typescript", "darwin", "npm")
        assert result == "npm install -g typescript"

    def test_snap_install_command(self):
        """Test snap install command generation."""
        from box_dump.commands.viewer import get_install_command

        result = get_install_command("code", "linux", "snap")
        assert result == "sudo snap install code"

    def test_flatpak_install_command(self):
        """Test flatpak install command generation."""
        from box_dump.commands.viewer import get_install_command

        result = get_install_command("org.freedesktop.Platform", "linux", "flatpak")
        assert result == "flatpak install org.freedesktop.Platform"

    def test_stew_install_command(self):
        """Test stew install command generation."""
        from box_dump.commands.viewer import get_install_command

        result = get_install_command("docker", "linux", "stew")
        assert result == "stew install docker"

    def test_zb_install_command(self):
        """Test zb install command generation."""
        from box_dump.commands.viewer import get_install_command

        result = get_install_command("kubectl", "linux", "zb")
        assert result == "zb install kubectl"

    def test_default_darwin(self):
        """Test default install command for macOS."""
        from box_dump.commands.viewer import get_install_command

        result = get_install_command("neovim", "darwin", None)
        assert result == "brew install neovim"

    def test_default_linux(self):
        """Test default install command for Linux."""
        from box_dump.commands.viewer import get_install_command

        result = get_install_command("git", "linux", None)
        assert result == "sudo apt install git"


class TestLoadPackages:
    """Tests for loading packages from JSON files."""

    def test_load_packages_from_repo(self, tmp_path):
        """Test loading packages from JSON files."""
        from box_dump.commands.viewer import load_packages_from_repo

        (tmp_path / "JesseDev_brew.json").write_text(
            json.dumps(
                [
                    {"name": "neovim", "version": "0.9.5"},
                    {"name": "fish", "version": "3.6.0"},
                ]
            )
        )
        (tmp_path / "UbuntuServer_apt.json").write_text(
            json.dumps(
                [
                    {"name": "git", "version": "2.43.0"},
                ]
            )
        )

        with patch("box_dump.commands.viewer.LOCAL_REPO_PATH", tmp_path):
            result = load_packages_from_repo()

        assert "JesseDev" in result
        assert "UbuntuServer" in result
        assert result["JesseDev"]["brew"][0]["name"] == "neovim"
        assert result["UbuntuServer"]["apt"][0]["name"] == "git"
