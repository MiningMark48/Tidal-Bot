import filecmp
import os
import shutil
from os import path
from datetime import datetime as dt
from util.logger import Logger


def backup_file(filename: str):
    date = dt.now()
    folder_name = "backups"
    subfolder_name = f"{date.strftime('%m%d%y')}"
    backup_name = f"{folder_name}/{subfolder_name}/{filename}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    if not os.path.exists(f"{folder_name}/{subfolder_name}"):
        os.makedirs(f"{folder_name}/{subfolder_name}")

    if path.exists(filename) and path.exists(backup_name):
        if filecmp.cmp(filename, backup_name):
            # print(f"{filename} is same as {backup_name}, skipping...")
            return

    shutil.copyfile(f"{filename}", backup_name)
    Logger.info(f"Backed up {filename} to {backup_name}")
