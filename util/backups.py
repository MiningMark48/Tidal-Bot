import os
import shutil


def backup_file(filename: str):
    folder_name = "backups"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    shutil.copyfile(f"{filename}", f"{folder_name}/{filename}")
    print(f"Backed up {filename} to {folder_name}/{filename}")
