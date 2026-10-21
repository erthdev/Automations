# ============================================================
# FILE ORGANIZER
# ============================================================

import os
import shutil
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

# Directory to be organized
TARGET_DIRECTORY = Path.home() / "Downloads"

listOfDirectories = {
    "Picture_Folder": [".jpeg", ".jpg", ".gif", ".png"],
    "Video_Folder": [".wmv", ".mov", ".mp4", ".mpg", ".mpeg", ".mkv"],
    "Zip_Folder": [".iso", ".tar", ".gz", ".rz", ".7z", ".dmg", ".rar", ".zip"],
    "Music_Folder": [".mp3", ".msv", ".wav", ".wma"],
    "PDF_Folder": [".pdf"],
}

# Map file extensions to folder names
fileFormatDictionary = {
    extension: folder
    for folder, extensions in listOfDirectories.items()
    for extension in extensions
}

# ============================================================
# ORGANIZER FUNCTION
# ============================================================

def organizer():

    if not TARGET_DIRECTORY.is_dir():
        print(f"Directory does not exist: {TARGET_DIRECTORY}")
        return

    print(f"Organizing files in: {TARGET_DIRECTORY}")

    try:
        with os.scandir(TARGET_DIRECTORY) as entries:
            for entry in entries:

                # Skip directories
                if entry.is_dir():
                    continue

                filePath = Path(entry.path)

                # Get file extensions
                finalFileFormat = filePath.suffix.lower()

                # Find appropriate folder
                directoryName = fileFormatDictionary.get(
                    finalFileFormat, "Other_Folder"
                )

                directoryPath = TARGET_DIRECTORY / directoryName

                try:
                    # Create folder if it doesn't exist
                    directoryPath.mkdir(exist_ok=True)

                    # Build the destination path
                    destination = directoryPath / filePath.name

                    # Avoid overwriting existing files
                    if destination.exists():
                        print(
                            f"Skipped: {filePath.name} "
                            "(destination already exists)"
                        )
                        continue

                    # Move the file
                    shutil.move(str(filePath), str(destination))

                    print(
                        f"Moved: {filePath.name} -> {directoryName}"
                    )

                except OSError as error:
                    print(f"Failed to move {filePath.name}: {error}")

    except OSError as error:
        print(f"Unable to scan directory: {error}")

    print("File organization complete!")


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":
    organizer()
