"""The installer."""

from __future__ import annotations

import logging
import re
import shutil
import subprocess

from pathlib import Path
from typing import TYPE_CHECKING

from .utils import builder_introspect, note, oxford_join, subprocess_run


if TYPE_CHECKING:
    from .config import Config


logger = logging.getLogger(__name__)


class Installer:
    """The installer class."""

    def __init__(self: Installer, config: Config) -> None:
        """Initialize the installer.

        Args:
            config: The application configuration.
        """
        self._config = config

    def run(self: Installer) -> None:
        """Run the installer."""
        self._install_core()
        if self._config.collection_local:
            self._install_local_collection()
            if self._config.args.editable:
                self._swap_editable_collection()
        else:
            self._install_galaxy_collection()

        builder_introspect(config=self._config)
        self._pip_install()
        self._check_bindep()

        if self._config.args.venv and (
            self._config.interpreter != self._config.venv_interpreter
        ):
            msg = "A virtual environment was specified but has not been activated."
            logger.warning(msg)
            msg = (
                "Please activate the virtual environment:"
                f"\nsource {self._config.args.venv}/bin/activate"
            )
            logger.warning(msg)

    def _install_core(self: Installer) -> None:
        """Install ansible-core if not installed already."""
        core = self._config.venv_bindir / "ansible"
        if core.exists():
            return
        msg = "Installing ansible-core."
        logger.debug(msg)
        command = f"{self._config.venv_interpreter} -m pip install ansible-core"
        try:
            subprocess_run(command=command, verbose=self._config.args.verbose)
        except subprocess.CalledProcessError as exc:
            err = f"Failed to install ansible-core: {exc}"
            logger.critical(err)

    def _install_galaxy_collection(self: Installer) -> None:
        """Install the collection from galaxy."""
        if self._config.site_pkg_collection_path.exists():
            msg = f"Removing installed {self._config.site_pkg_collection_path}"
            logger.debug(msg)
            if self._config.site_pkg_collection_path.is_symlink():
                self._config.site_pkg_collection_path.unlink()
            else:
                shutil.rmtree(self._config.site_pkg_collection_path)

        command = (
            f"{self._config.venv_bindir / 'ansible-galaxy'} collection"
            f" install {self._config.collection_name}"
            f" -p {self._config.site_pkg_path}"
            " --force"
        )
        env = {
            "ANSIBLE_GALAXY_COLLECTIONS_PATH_WARNING": str(self._config.args.verbose),
        }
        msg = "Running ansible-galaxy to install non-local collection and it's dependencies."
        logger.debug(msg)
        try:
            proc = subprocess_run(
                command=command,
                env=env,
                verbose=self._config.args.verbose,
            )
        except subprocess.CalledProcessError as exc:
            err = f"Failed to install collection: {exc} {exc.stderr}"
            logger.critical(err)
            return
        installed = re.findall(r"(\w+\.\w+):.*installed", proc.stdout)
        msg = f"Installed collections: {oxford_join(installed)}"
        note(msg)

    def _install_local_collection(self: Installer) -> None:  # noqa: PLR0912
        """Install the collection from the build directory."""
        command = (
            "cp -r --parents $(git ls-files 2> /dev/null || ls)"
            f" {self._config.collection_build_dir}"
        )
        msg = "Copying collection to build directory using git ls-files."
        logger.debug(msg)
        try:
            subprocess_run(
                command=command,
                cwd=self._config.collection_path,
                verbose=self._config.args.verbose,
            )
        except subprocess.CalledProcessError as exc:
            err = f"Failed to copy collection to build directory: {exc} {exc.stderr}"
            logger.critical(err)

        command = (
            f"cd {self._config.collection_build_dir} &&"
            f" {self._config.venv_bindir / 'ansible-galaxy'} collection build"
            f" --output-path {self._config.collection_build_dir}"
            " --force"
        )

        msg = "Running ansible-galaxy to build collection."
        logger.debug(msg)

        try:
            subprocess_run(command=command, verbose=self._config.args.verbose)
        except subprocess.CalledProcessError as exc:
            err = f"Failed to build collection: {exc} {exc.stderr}"
            logger.critical(err)

        built = [
            f
            for f in Path(self._config.collection_build_dir).iterdir()
            if f.is_file() and f.name.endswith(".tar.gz")
        ]
        if len(built) != 1:
            err = (
                "Expected to find one collection tarball in"
                f"{self._config.collection_build_dir}, found {len(built)}"
            )
            raise RuntimeError(err)
        tarball = built[0]

        if self._config.site_pkg_collection_path.exists():
            msg = f"Removing installed {self._config.site_pkg_collection_path}"
            logger.debug(msg)
            if self._config.site_pkg_collection_path.is_symlink():
                self._config.site_pkg_collection_path.unlink()
            else:
                shutil.rmtree(self._config.site_pkg_collection_path)

        info_dirs = [
            entry
            for entry in self._config.site_pkg_collections_path.iterdir()
            if entry.is_dir()
            and entry.name.endswith(".info")
            and entry.name.startswith(self._config.collection_name)
        ]
        for info_dir in info_dirs:
            msg = f"Removing installed {info_dir}"
            logger.debug(msg)
            shutil.rmtree(info_dir)

        command = (
            f"{self._config.venv_bindir / 'ansible-galaxy'} collection"
            f" install {tarball} -p {self._config.site_pkg_path}"
            " --force"
        )
        env = {
            "ANSIBLE_GALAXY_COLLECTIONS_PATH_WARNING": str(self._config.args.verbose),
        }
        msg = "Running ansible-galaxy to install a local collection and it's dependencies."
        logger.debug(msg)
        try:
            proc = subprocess_run(
                command=command,
                env=env,
                verbose=self._config.args.verbose,
            )
        except subprocess.CalledProcessError as exc:
            err = f"Failed to install collection: {exc} {exc.stderr}"
            logger.critical(err)
            return

        # ansible-galaxy collection install does not include the galaxy.yml for version
        # nor does it create an info file that can be used to determine the version.
        # preserve the MANIFEST.json file for editable installs
        if not self._config.args.editable:
            shutil.copy(
                self._config.collection_build_dir / "galaxy.yml",
                self._config.site_pkg_collection_path / "galaxy.yml",
            )
        else:
            shutil.copy(
                self._config.site_pkg_collection_path / "MANIFEST.json",
                self._config.collection_cache_dir / "MANIFEST.json",
            )

        installed = re.findall(r"(\w+\.\w+):.*installed", proc.stdout)
        msg = f"Installed collections: {oxford_join(installed)}"
        note(msg)

    def _swap_editable_collection(self: Installer) -> None:
        """Swap the installed collection with the current working directory."""
        msg = f"Removing installed {self._config.site_pkg_collection_path}"
        logger.debug(msg)
        if self._config.site_pkg_collection_path.exists():
            if self._config.site_pkg_collection_path.is_symlink():
                self._config.site_pkg_collection_path.unlink()
            else:
                shutil.rmtree(self._config.site_pkg_collection_path)

        msg = (
            f"Symlinking {self._config.site_pkg_collection_path}"
            f" to {self._config.collection_path}"
        )
        logger.debug(msg)
        self._config.site_pkg_collection_path.symlink_to(self._config.collection_path)

    def _pip_install(self: Installer) -> None:
        """Install the dependencies."""
        command = (
            f"{self._config.venv_interpreter} -m pip install"
            f" -r {self._config.discovered_python_reqs}"
        )

        msg = (
            f"Installing python requirements from {self._config.discovered_python_reqs}"
        )
        logger.debug(msg)
        try:
            subprocess_run(command=command, verbose=self._config.args.verbose)
        except subprocess.CalledProcessError as exc:
            err = (
                "Failed to install requirements from"
                f" {self._config.discovered_python_reqs}: {exc}"
            )
            raise RuntimeError(err) from exc
        else:
            msg = "All python requirements are installed."
            note(msg)

    def _check_bindep(self: Installer) -> None:
        """Check the bindep file."""
        command = f"bindep -b -f {self._config.discovered_bindep_reqs}"
        try:
            subprocess_run(command=command, verbose=self._config.args.verbose)
        except subprocess.CalledProcessError as exc:
            lines = exc.stdout.splitlines()
            msg = (
                "Required system packages are missing."
                " Please use the system package manager to install them."
            )
            logger.warning(msg)
            for line in lines:
                msg = f"Missing: {line}"
                logger.warning(msg)
                pass
        else:
            msg = "All required system packages are installed."
            logger.debug(msg)
            return
