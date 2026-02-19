import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import List

import pytest


def run(cmd: List[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a command and return the completed process."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result


def test_cli_help() -> None:
    """Test that the CLI help command works."""
    result = run([sys.executable, "-m", "hatch_jupyter_kernels", "--help"])
    assert result.returncode == 0
    assert "show this help message and exit" in result.stdout


def test_cli_install_uninstall() -> None:
    """Test the CLI install and uninstall commands."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        kernel_name = "test_kernel"
        env_name = "test_env"

        # Create a dummy environment
        env_path = tmp_path / env_name
        run([sys.executable, "-m", "venv", str(env_path)])

        # Install the kernel
        install_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "install",
            "--name",
            kernel_name,
            "--env",
            str(env_path),
            "--prefix",
            str(tmp_path),
        ]
        result = run(install_cmd)
        assert result.returncode == 0
        assert "Kernel installed successfully" in result.stdout

        # Check that the kernel spec file exists
        kernel_dir = Path(tmp_path) / "share" / "jupyter" / "kernels" / kernel_name
        assert kernel_dir.exists()
        assert (kernel_dir / "kernel.json").exists()

        # Uninstall the kernel
        uninstall_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "uninstall",
            "--name",
            kernel_name,
            "--prefix",
            str(tmp_path),
        ]
        result = run(uninstall_cmd)
        assert result.returncode == 0
        assert "Kernel uninstalled successfully" in result.stdout

        # Check that the kernel spec file is removed
        assert not kernel_dir.exists()


def test_cli_install_uninstall_user() -> None:
    """Test the CLI install and uninstall commands with --user."""
    kernel_name = "test_kernel_user"
    env_name = "test_env_user"

    # Determine the user's jupyter kernels directory
    result = run([sys.executable, "-m", "jupyter", "kernelspec", "list"])
    assert result.returncode == 0
    user_kernel_dir = Path(result.stdout.splitlines()[1].strip())

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a dummy environment
        env_path = tmp_path / env_name
        run([sys.executable, "-m", "venv", str(env_path)])

        # Install the kernel with --user
        install_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "install",
            "--name",
            kernel_name,
            "--env",
            str(env_path),
            "--user",
        ]
        result = run(install_cmd)
        assert result.returncode == 0
        assert "Kernel installed successfully" in result.stdout

        # Check that the kernel spec file exists in the user's directory
        kernel_dir = user_kernel_dir / kernel_name
        assert kernel_dir.exists()
        assert (kernel_dir / "kernel.json").exists()

        # Uninstall the kernel with --user
        uninstall_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "uninstall",
            "--name",
            kernel_name,
            "--user",
        ]
        result = run(uninstall_cmd)
        assert result.returncode == 0
        assert "Kernel uninstalled successfully" in result.stdout

        # Check that the kernel spec file is removed from the user's directory
        assert not kernel_dir.exists()


def test_cli_install_display_name() -> None:
    """Test the CLI install command with --display-name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        kernel_name = "test_kernel_display"
        env_name = "test_env_display"
        display_name = "My Custom Kernel"

        # Create a dummy environment
        env_path = tmp_path / env_name
        run([sys.executable, "-m", "venv", str(env_path)])

        # Install the kernel with --display-name
        install_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "install",
            "--name",
            kernel_name,
            "--env",
            str(env_path),
            "--prefix",
            str(tmp_path),
            "--display-name",
            display_name,
        ]
        result = run(install_cmd)
        assert result.returncode == 0
        assert "Kernel installed successfully" in result.stdout

        # Check that the kernel spec file exists
        kernel_dir = Path(tmp_path) / "share" / "jupyter" / "kernels" / kernel_name
        assert kernel_dir.exists()
        kernel_json_path = kernel_dir / "kernel.json"
        assert kernel_json_path.exists()

        # Verify the display name in the kernel.json file
        import json

        with open(kernel_json_path, "r") as f:
            kernel_json = json.load(f)
        assert kernel_json["display_name"] == display_name

        # Uninstall the kernel
        uninstall_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "uninstall",
            "--name",
            kernel_name,
            "--prefix",
            str(tmp_path),
        ]
        result = run(uninstall_cmd)
        assert result.returncode == 0
        assert "Kernel uninstalled successfully" in result.stdout

        # Check that the kernel spec file is removed
        assert not kernel_dir.exists()


def test_cli_install_executable() -> None:
    """Test the CLI install command with --executable."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        kernel_name = "test_kernel_executable"
        env_name = "test_env_executable"
        executable_path = tmp_path / "custom_python"
        executable_path.write_text("#!/bin/bash\nexec python \"$@\"", encoding="utf-8")
        executable_path.chmod(0o755)

        # Create a dummy environment
        env_path = tmp_path / env_name
        run([sys.executable, "-m", "venv", str(env_path)])

        # Install the kernel with --executable
        install_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "install",
            "--name",
            kernel_name,
            "--env",
            str(env_path),
            "--prefix",
            str(tmp_path),
            "--executable",
            str(executable_path),
        ]
        result = run(install_cmd)
        assert result.returncode == 0
        assert "Kernel installed successfully" in result.stdout

        # Check that the kernel spec file exists
        kernel_dir = Path(tmp_path) / "share" / "jupyter" / "kernels" / kernel_name
        assert kernel_dir.exists()
        kernel_json_path = kernel_dir / "kernel.json"
        assert kernel_json_path.exists()

        # Verify the executable path in the kernel.json file
        import json

        with open(kernel_json_path, "r") as f:
            kernel_json = json.load(f)
        assert kernel_json["argv"][0] == str(executable_path)

        # Uninstall the kernel
        uninstall_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "uninstall",
            "--name",
            kernel_name,
            "--prefix",
            str(tmp_path),
        ]
        result = run(uninstall_cmd)
        assert result.returncode == 0
        assert "Kernel uninstalled successfully" in result.stdout

        # Check that the kernel spec file is removed
        assert not kernel_dir.exists()


def test_cli_install_missing_env() -> None:
    """Test the CLI install command with a missing environment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        kernel_name = "test_kernel_missing_env"
        env_name = "missing_env"

        # Install the kernel with a missing environment
        install_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "install",
            "--name",
            kernel_name,
            "--env",
            str(tmp_path / env_name),
            "--prefix",
            str(tmp_path),
        ]
        result = run(install_cmd)
        assert result.returncode != 0
        assert "The environment path does not exist" in result.stderr


def test_cli_uninstall_missing_kernel() -> None:
    """Test the CLI uninstall command with a missing kernel."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        kernel_name = "missing_kernel"

        # Uninstall the kernel with a missing kernel
        uninstall_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "uninstall",
            "--name",
            kernel_name,
            "--prefix",
            str(tmp_path),
        ]
        result = run(uninstall_cmd)
        assert result.returncode != 0
        assert "The kernel spec directory does not exist" in result.stderr


def test_cli_install_env_not_venv() -> None:
    """Test the CLI install command when the environment is not a venv."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        kernel_name = "test_kernel_not_venv"
        env_path = tmp_path / "not_a_venv"
        env_path.mkdir()

        # Install the kernel with an environment that is not a venv
        install_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "install",
            "--name",
            kernel_name,
            "--env",
            str(env_path),
            "--prefix",
            str(tmp_path),
        ]
        result = run(install_cmd)
        assert result.returncode != 0
        assert "The environment path is not a venv" in result.stderr


def test_cli_install_no_name() -> None:
    """Test the CLI install command with no kernel name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        env_name = "test_env_no_name"

        # Create a dummy environment
        env_path = tmp_path / env_name
        run([sys.executable, "-m", "venv", str(env_path)])

        # Install the kernel with no name
        install_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "install",
            "--env",
            str(env_path),
            "--prefix",
            str(tmp_path),
        ]
        result = run(install_cmd)
        assert result.returncode != 0
        assert "You must specify a kernel name" in result.stderr


def test_cli_uninstall_no_name() -> None:
    """Test the CLI uninstall command with no kernel name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Uninstall the kernel with no name
        uninstall_cmd = [
            sys.executable,
            "-m",
            "hatch_jupyter_kernels",
            "uninstall",
            "--prefix",
            str(tmp_path),
        ]
        result = run(uninstall_cmd)
        assert result.returncode != 0
        assert "You must specify a kernel name" in result.stderr