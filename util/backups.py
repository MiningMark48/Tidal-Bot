import filecmp
import os
import shutil
from os import path


def backup_file(filename: str):
    folder_name = "backups"
    backup_name = f"{folder_name}/{filename}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    if path.exists(filename) and path.exists(backup_name):
        if filecmp.cmp(filename, backup_name):
            print(f"{filename} is same as {backup_name}, skipping...")
            return

    shutil.copyfile(f"{filename}", backup_name)
    print(f"Backed up {filename} to {backup_name}")
