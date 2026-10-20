#!/usr/bin/env python3

"""
Linux Program & Download Inventory

Scans common Linux application/package sources and downloaded
program files.

Designed for Linux Mint / Ubuntu-based systems.

Author: Me:>
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

HOME = Path.home()

DOWNLOADS = HOME / "Downloads"

# Common places where manually installed applications may live
PROGRAM_LOCATIONS = [
    HOME / "Applications",
    HOME / "bin",
    Path("/opt"),
    Path("/usr/local/bin"),
]

# Files that may represent downloadable/installable programs
PROGRAM_EXTENSIONS = {
    ".deb",
    ".rpm",
    ".appimage",
    ".flatpak",
    ".snap",
    ".run",
    ".sh",
    ".bin",
    ".jar",
    ".tar",
    ".tar.gz",
    ".tar.xz",
    ".tar.bz2",
    ".zip",
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def print_section(title):
    """Print a formatted section heading."""

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def command_exists(command):
    """Check whether a Linux command exists."""

    return shutil.which(command) is not None


def run_command(command):
    """
    Run a command and return its output.

    Returns an empty list if the command fails.
    """

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout.strip().splitlines()

    except (subprocess.SubprocessError, FileNotFoundError):

        return []


def format_size(size):
    """Convert bytes into a human-readable size."""

    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:

        if size < 1024:

            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


# ============================================================
# APT / DPKG
# ============================================================

def get_apt_packages():

    packages = []

    if not command_exists("dpkg"):

        return packages

    output = run_command(
        ["dpkg-query", "-W", "-f=${binary:Package}\\t${Version}\\n"]
    )

    for line in output:

        if "\t" in line:

            name, version = line.split("\t", 1)

            packages.append({
                "name": name,
                "version": version
            })

    return packages


# ============================================================
# FLATPAK
# ============================================================

def get_flatpak_apps():

    apps = []

    if not command_exists("flatpak"):

        return apps

    output = run_command(
        [
            "flatpak",
            "list",
            "--app",
            "--columns=application,version,name"
        ]
    )

    for line in output:

        parts = line.split("\t")

        if len(parts) >= 3:

            apps.append({
                "id": parts[0],
                "version": parts[1],
                "name": parts[2]
            })

    return apps


# ============================================================
# SNAP
# ============================================================

def get_snap_packages():

    packages = []

    if not command_exists("snap"):

        return packages

    output = run_command(
        ["snap", "list"]
    )

    # Skip header
    for line in output[1:]:

        parts = line.split()

        if len(parts) >= 2:

            packages.append({
                "name": parts[0],
                "version": parts[1]
            })

    return packages


# ============================================================
# DOWNLOADED PROGRAM FILES
# ============================================================

def find_downloaded_programs():

    results = []

    if not DOWNLOADS.exists():

        return results

    for file in DOWNLOADS.rglob("*"):

        if not file.is_file():

            continue

        name = file.name.lower()

        # Handle multi-part extensions first
        if (
            name.endswith(".tar.gz")
            or name.endswith(".tar.xz")
            or name.endswith(".tar.bz2")
        ):

            extension = ".archive"

        else:

            extension = file.suffix.lower()

        if extension in PROGRAM_EXTENSIONS:

            try:

                size = file.stat().st_size

                modified = datetime.fromtimestamp(
                    file.stat().st_mtime
                )

                results.append({
                    "name": file.name,
                    "path": file,
                    "size": size,
                    "modified": modified,
                    "type": extension
                })

            except (PermissionError, FileNotFoundError):

                pass

    return results


# ============================================================
# EXECUTABLE FILES
# ============================================================

def find_executables():

    results = []

    for location in PROGRAM_LOCATIONS:

        if not location.exists():

            continue

        try:

            for file in location.rglob("*"):

                if not file.is_file():

                    continue

                try:

                    if os.access(file, os.X_OK):

                        results.append(file)

                except PermissionError:

                    pass

        except PermissionError:

            pass

    return results


# ============================================================
# PATH COMMANDS
# ============================================================

def get_path_directories():

    return os.environ.get(
        "PATH",
        ""
    ).split(os.pathsep)


def find_common_commands():

    commands = [
        "python3",
        "git",
        "gcc",
        "g++",
        "node",
        "npm",
        "docker",
        "vim",
        "nano",
        "curl",
        "wget",
        "ffmpeg",
        "java",
        "go",
        "rustc",
        "cargo",
    ]

    found = []

    for command in commands:

        location = shutil.which(command)

        if location:

            found.append({
                "command": command,
                "location": location
            })

    return found


# ============================================================
# DISPLAY
# ============================================================

def show_apt_packages(packages):

    print_section(
        f"📦 APT / DPKG PACKAGES ({len(packages)})"
    )

    for package in packages:

        print(
            f"{package['name']:<45}"
            f"{package['version']}"
        )


def show_flatpak_apps(apps):

    print_section(
        f"📦 FLATPAK APPLICATIONS ({len(apps)})"
    )

    for app in apps:

        print(
            f"{app['name']:<35}"
            f"{app['version']:<20}"
            f"{app['id']}"
        )


def show_snap_packages(packages):

    print_section(
        f"📦 SNAP PACKAGES ({len(packages)})"
    )

    for package in packages:

        print(
            f"{package['name']:<35}"
            f"{package['version']}"
        )


def show_downloads(files):

    print_section(
        f"⬇️ DOWNLOADED PROGRAM FILES ({len(files)})"
    )

    for file in files:

        print(
            f"{file['name']:<35}"
            f"{format_size(file['size']):>12}    "
            f"{file['path']}"
        )


def show_executables(files):

    print_section(
        f"⚙️ MANUALLY INSTALLED / EXECUTABLE FILES ({len(files)})"
    )

    for file in files:

        print(file)


def show_commands(commands):

    print_section(
        f"🛠️ COMMON COMMAND-LINE PROGRAMS ({len(commands)})"
    )

    for command in commands:

        print(
            f"{command['command']:<15}"
            f"{command['location']}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("🐧 LINUX PROGRAM & DOWNLOAD INVENTORY")
    print("=" * 70)

    print(
        f"Computer: {os.uname().nodename}"
    )

    print(
        f"User:     {HOME.name}"
    )

    print(
        f"Date:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # --------------------------------------------------------
    # APT
    # --------------------------------------------------------

    apt_packages = get_apt_packages()

    show_apt_packages(
        apt_packages
    )

    # --------------------------------------------------------
    # Flatpak
    # --------------------------------------------------------

    flatpak_apps = get_flatpak_apps()

    show_flatpak_apps(
        flatpak_apps
    )

    # --------------------------------------------------------
    # Snap
    # --------------------------------------------------------

    snap_packages = get_snap_packages()

    show_snap_packages(
        snap_packages
    )

    # --------------------------------------------------------
    # Downloaded installers
    # --------------------------------------------------------

    downloaded_files = find_downloaded_programs()

    show_downloads(
        downloaded_files
    )

    # --------------------------------------------------------
    # Manually installed programs
    # --------------------------------------------------------

    executables = find_executables()

    show_executables(
        executables
    )

    # --------------------------------------------------------
    # Common command-line tools
    # --------------------------------------------------------

    commands = find_common_commands()

    show_commands(
        commands
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print_section("📊 SUMMARY")

    print(
        f"APT packages              : {len(apt_packages)}"
    )

    print(
        f"Flatpak applications      : {len(flatpak_apps)}"
    )

    print(
        f"Snap packages             : {len(snap_packages)}"
    )

    print(
        f"Downloaded program files  : {len(downloaded_files)}"
    )

    print(
        f"Manual executables        : {len(executables)}"
    )

    print(
        f"Known CLI tools           : {len(commands)}"
    )

    print()
    print("✅ Scan complete.")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
